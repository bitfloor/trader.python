#!/usr/bin/env python
# will add a random order and then cancel it immediately

import random
import math

import args

bitfloor = args.get_rapi()

count = 0
while True:
    if count % 1000 == 0:
        try:
            center = float(bitfloor.ticker()['price'])
        except:
            center = 5
        magnitude = math.ceil(center/5)
        print '{0} order/cancels: {1}, {2}'.format(count, center, magnitude)

    # add order
    side = random.randrange(2)
    price = bitfloor.round_inc(max(0.05, random.normalvariate(center - 0.5 + side, magnitude)))
    size = round(max(0.01, random.random())*1e8)/1e8

    resp = bitfloor.order_new(side=side, size=size, price=price)
    id = resp.get('order_id')
    if id:
        bitfloor.order_cancel(id)
    else:
        print "ERROR:", resp

    count += 1

