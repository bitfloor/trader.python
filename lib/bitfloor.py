import hmac
import hashlib
import base64
import urllib
import httplib
import time
import json
import json_ascii
import copy
from decimal import Decimal
import decimal
import os

with open(os.path.join(os.path.dirname(__file__), '../config.json')) as f:
    config = json.load(f, object_hook=json_ascii.decode_dict)

if config['data_port'] == 443 and config['order_port'] == 443:
    HTTPConn = httplib.HTTPSConnection
else:
    HTTPConn = httplib.HTTPConnection # for local testing only

class RAPI(object):
    def __init__(self, product_id, key, secret):
        self._key = key
        self._secret = secret
        self._product_id = product_id
        self._inc = Decimal('0.05') # TODO: get from bitfloor

    def book(self, level=1):
        url = '/book/L{1}/{0}'.format(self._product_id, level)
        return self._send_get(url)

    def ticker(self):
        url = '/ticker/{0}'.format(self._product_id)
        return self._send_get(url)

    def trades(self):
        url = '/history/{0}'.format(self._product_id)
        return self._send_get(url)

    def order_new(self, side, size, price):
        return self._send_post('/order/new', {
            'product_id': self._product_id,
            'side': side,
            'size': size,
            'price': price
        })

    def buy(self, **kwargs):
        return self.order_new(side=0, **kwargs)

    def sell(self, **kwargs):
        return self.order_new(side=1, **kwargs)

    def order_cancel(self, order_id):
        return self._send_post('/order/cancel', {
            'product_id': self._product_id,
            'order_id': order_id
        })

    def orders(self):
        return self._send_post('/orders')

    def accounts(self):
        return self._send_post('/accounts')

    def floor_inc(self, n):
        return (Decimal(str(n))/self._inc).quantize(Decimal('1'), rounding=decimal.ROUND_DOWN)*self._inc

    def ceil_inc(self, n):
        return (Decimal(str(n))/self._inc).quantize(Decimal('1'), rounding=decimal.ROUND_UP)*self._inc

    def round_inc(self, n):
        return (Decimal(str(n))/self._inc).quantize(Decimal('1'))*self._inc

    def _send_get(self, url, payload={}):
        body = urllib.urlencode(payload)
        conn = HTTPConn(config['host'], config['data_port'])
        conn.request("GET", url, body)
        resp = conn.getresponse()
        s = resp.read()
        conn.close()
        return json.loads(s, object_hook=json_ascii.decode_dict)

    def _send_post(self, url, payload={}):
        payload = copy.copy(payload) # avoid modifying the original dict

        # add some stuff to the payload
        payload['nonce'] = int(time.time()*1e6)

        body = urllib.urlencode(payload)

        sig = hmac.new(self._secret, body, hashlib.sha512).digest()
        sig_b64 = base64.b64encode(sig)

        headers = {
            'bitfloor-key': self._key,
            'bitfloor-sign': sig_b64,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': len(body)
        }

        conn = HTTPConn(config['host'], config['order_port'])
        conn.request("POST", url, body, headers)
        resp = conn.getresponse()
        s = resp.read()
        conn.close()
        return json.loads(s, object_hook=json_ascii.decode_dict)

