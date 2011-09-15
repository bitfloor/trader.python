import sys
import os
import json
import json_ascii
from bitfloor import RAPI

def get_rapi():
    print 
    if len(sys.argv) < 3: # awww, it's a heart!
        print "Usage: {0} product_id keyfile".format(sys.argv[0])
        sys.exit(1)

    product_id, keyfile = sys.argv[1:]

    path = os.path.join(os.path.join(os.path.dirname(__file__), '../keys'), keyfile + '.json')
    with open(path) as f:
        config = json.load(f, object_hook=json_ascii.decode_dict)

    return RAPI(product_id=product_id, key=config['key'], secret=config['secret'])