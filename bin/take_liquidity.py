#!/usr/bin/env python
# randomly adds/cancels orders
# keeps track of average latency of ordering and cancelling

import random
import math
import time

import args

bitfloor = args.get_rapi()

olatency = [] # order latency
clatency = [] # cancel latency

while True:
    # add order
    book = bitfloor.book()
    side = random.randrange(2)
    if side == 0:
        price = float(book['ask'][0])*1.1
    else:
        price = float(book['bid'][0])*.9

    price = bitfloor.round_inc(price)

    size = round(max(0.01, 10*random.random())*1e8)/1e8

    order = bitfloor.order_new(side=side, size=size, price=price)
    id = order.get('order_id')
    if not id:
        print "ERROR:", order

    time.sleep(1)
