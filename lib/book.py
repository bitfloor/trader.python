# will parse any json book in standard form

import decimal
from decimal import Decimal

class Order(object):
    def __init__(self, size, price):
        self.size = size
        self.price = price

    def __repr__(self):
        return "{0}@{1}".format(self.size, self.price)

class Book(object):
    @classmethod
    def parse(cls, d):
        def parse_side(arr):
            orders = []
            for a in arr:
                size = Decimal(str(a[1]))
                price = Decimal(str(a[0]))
                orders.append(Order(size, price))
            return orders

        bids = parse_side(d['bids'])
        asks = parse_side(d['asks'])

        return cls(bids, asks)

    def __init__(self, bids, asks):
        self.bids = bids
        self.asks = asks

    def sort(self):
        self.bids.sort(key=lambda o: o.price, reverse=True)
        self.asks.sort(key=lambda o: o.price)

    def flatten(self, increment):
        def floor_inc(n):
            return (Decimal(str(n))/Decimal(increment)).quantize(Decimal('1'), rounding=decimal.ROUND_DOWN)*Decimal(increment)
        def ceil_inc(n):
            return (Decimal(str(n))/Decimal(increment)).quantize(Decimal('1'), rounding=decimal.ROUND_UP)*Decimal(increment)

        bids = {}
        asks = {}

        def add(d, price, size):
            o = d.get(price)
            if o is None:
                d[price] = Order(size, price)
            else:
                o.size += size


        for o in self.bids:
            price = floor_inc(o.price)
            add(bids, price, o.size)

        for o in self.asks:
            price = ceil_inc(o.price)
            add(asks, price, o.size)

        self.bids = bids.values()
        self.asks = asks.values()

    def subtract(self, other):
        bids = {}
        asks = {}
        for o in self.bids:
            bids[o.price] = o
        for o in self.asks:
            asks[o.price] = o

        def subtract_size(d, price, size):
            o = d.get(price)
            if o is not None:
                o.size -= size
            else:
                d[price] = Order(-size, price)

        # remove order sizes book
        if other:
            for o in other.bids:
                subtract_size(bids, o.price, o.size)
            for o in other.asks:
                subtract_size(asks, o.price, o.size)

        self.bids = bids.values()
        self.asks = asks.values()
