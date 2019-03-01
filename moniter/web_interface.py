#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 12:59:26
__author__ = "chenwx"

import requests
import yaml
import redis
import time
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool

conf_file = str(Path(__file__).resolve().parent / "conf.yaml")
conf_data = yaml.load(open(conf_file, "r").read())

def request_url(name, url):
    try:
        r = requests.get(url, timeout=1)
        code = r.status_code
        r.close()
    except Exception as e:
        code = 9

    mess = {
        'name': name,
        'url': url,
        'status': code,
        'ctime': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return mess

def task_run(url_list):
    pool = ThreadPool(50)
    result = []
    for name, url in url_list.items():
        result.append(pool.apply_async(request_url, (name, url)))
    pool.close()
    pool.join()

    Display = []
    for res in result:
        vle = res.get()
        if vle != 0:
            Display.append(vle)
    return Display

def set_redis(value, mess_code):
    redis_conf = conf_data.get("redis")
    redis_host = redis_conf.get("host")
    redis_port = redis_conf.get("port")
    redis_db = redis_conf.get("queue_db")
    r = redis.StrictRedis(
        host=redis_host, port=redis_port, db=redis_db, decode_responses=True
    )
    key = 'queue:bunnyc'
    data = {
        'mess_code': mess_code,
        'type': 'web_service',
        'body': value
    }
    r.rpush(key, str(data))

web_service = conf_data.get("web_service")
data = task_run(web_service)
set_redis(data, 2001)
