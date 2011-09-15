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

def mean(l):
    return float(sum(l))/len(l) if len(l) > 0 else None

orders = set()
count = 0
while True:
    if count % 1000 == 0:
        try:
            center = float(bitfloor.ticker()['price'])
        except:
            center = 5
        magnitude = math.ceil(center/5)
        print '{0} order/cancels: {1}, {2}'.format(count, center, magnitude)
        print 'latency: {0} orders, {1} cancels'.format(mean(olatency), mean(clatency))

    if random.random() < .5:
        if orders:
            start = time.time()
            bitfloor.order_cancel(orders.pop())
            clatency.append(time.time() - start)
    else:
        # add order
        side = random.randrange(2)
        price = bitfloor.round_inc(max(0.05, random.normalvariate(center - 0.05 + side/10, magnitude)))
        size = round(max(0.01, random.random())*1e8)/1e8

        start = time.time()
        order = bitfloor.order_new(side=side, size=size, price=price)
        olatency.append(time.time() - start)
        id = order.get('order_id')
        if id:
            orders.add(id)
        else:
            print "ERROR:", order

    count += 1
