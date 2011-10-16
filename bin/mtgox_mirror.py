#!/usr/bin/env python
# will try to mirror mtgox's order book,
# taking into account existing bitfloor orders and the user's available funds

import urllib
import json
import json_ascii
import decimal
from decimal import Decimal
import sys

from book import Book, Order

import args

bitfloor = args.get_rapi()
SIZE_LIMIT = 0.01

def get_mtgox():
    f = urllib.urlopen("http://mtgox.com/api/0/data/getDepth.php")
    return json.loads(f.read(), object_hook=json_ascii.decode_dict)

def get_funds():
    pos = {}
    bpositions = bitfloor.accounts()
    for p in bpositions:
        pos[p['currency']] = Decimal(str(p['amount']))
    return pos

def get_our_book():
    orders = bitfloor.orders()

    our_book = {
        'bids': {},
        'asks': {}
    }

    our_book2 = {
        'bids': [],
        'asks': []
    }

    for o in orders:
        size = Decimal(str(o['size']))
        price = Decimal(str(o['price']))
        order = Order(size, price)
        order.id = o['order_id'] # TODO: hacky
        tup = (str(price), str(size))
        if o['side'] == 0:
            our_book['bids'].setdefault(price, []).append(order)
            our_book2['bids'].append(tup)
        elif o['side'] == 1:
            our_book['asks'].setdefault(price, []).append(order)
            our_book2['asks'].append(tup)

    return our_book, Book.parse(our_book2)

def cancel(book, our_book, side):
    sides = side + 's'
    for o in getattr(book, sides):
        if o.size < -SIZE_LIMIT:
            for order in our_book[sides].get(o.price, []):
                print 'cancel ' + side, order
                bitfloor.order_cancel(order.id)
                o.size += order.size
                if o.size >= 0:
                    break

def run():
    mbook = Book.parse(get_mtgox())
    bbook = Book.parse(bitfloor.book(level=2))

    mbook.flatten('0.01')

    our_book, our_book2 = get_our_book()

    # remove our stuff from bbook
    # bbook will have the orders we don't control
    bbook.subtract(our_book2)

    # mbook will now have the gap needed to be filled by our orders
    mbook.subtract(bbook)

    funds = get_funds()

    # get the total remaining area needed to fill
    # find which factor of it we can fill with our total funds
    sumb = sum(o.price*o.size for o in mbook.bids if o.size > 0)*Decimal('1.04')
    bfactor = min(1, funds['USD']/sumb) if sumb > 0 else 1
    suma = sum(o.size for o in mbook.asks if o.size > 0)
    afactor = min(1, funds['BTC']/suma) if suma > 0 else 1

    print afactor, bfactor
    print suma, sumb

    # multiply everything positive by the factor
    # mbook will now have what we need to provide to bitfloor's book
    for o in mbook.bids:
        if o.size > 0:
            o.size *= bfactor
            o.size = o.size.quantize(Decimal('0.00000001'), rounding=decimal.ROUND_DOWN)
    for o in mbook.asks:
        if o.size > 0:
            o.size *= afactor
            o.size = o.size.quantize(Decimal('0.00000001'), rounding=decimal.ROUND_DOWN)

    # now, get the difference between what we need to provide and what we have
    mbook.subtract(our_book2)

    # cancel orders first which are above the gap
    cancel(mbook, our_book, 'bid')
    cancel(mbook, our_book, 'ask')

    # send in orders to fill the gaps
    for o in mbook.bids:
        if o.size > SIZE_LIMIT:
            print 'bid', o
            bitfloor.buy(size=str(o.size), price=str(o.price))
    for o in mbook.asks:
        if o.size > SIZE_LIMIT:
            print 'ask', o
            bitfloor.sell(size=str(o.size), price=str(o.price))

while True:
    try:
        run()
    except Exception as e:
        print >> sys.stderr, e
