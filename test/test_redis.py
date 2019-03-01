#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 12:59:26
__author__ = "chenwx"

import requests
import yaml
import redis
import time
import json
from pathlib import Path


def set_redis(value, mess_code):
    r = redis.StrictRedis(
        host='10.2.1.5', port=26379, db=0, decode_responses=True
    )
    key = 'queue:data'
    data = {
        'mess_code': mess_code,
        'body': value
    }
    r.rpush(key, data)

data = {
    'name': 'nihao',
    'num': 120
}

print(type(data))
a = json.dumps(data)
set_redis(json.loads(a), 2001)
