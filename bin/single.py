#!/usr/bin/env python
# adds a single order

import args
import cmd

bitfloor = args.get_rapi()

def trade(side, arg):
    try:
        size, price = arg.split()
        print bitfloor.order_new(side=side, size=size, price=price)
    except:
        print "Invalid arg {1}, expected size price".format(side, arg)

class Shell(cmd.Cmd):
    prompt = '(buy|sell size price) '

    def do_sell(self, arg):
        trade(1, arg)

    def do_buy(self, arg):
        trade(0, arg)

    def do_EOF(self, arg):
        print
        return True

Shell().cmdloop()
