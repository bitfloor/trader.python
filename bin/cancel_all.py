#!/usr/bin/env python
# cancels all the user's orders

import args

bitfloor = args.get_rapi()

orders = bitfloor.orders()
for order in orders:
    print bitfloor.order_cancel(order['order_id'])
