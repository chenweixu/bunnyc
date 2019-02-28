#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 12:59:26
__author__ = 'chenwx'

import requests
import yaml
import redis
import time
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool

conf_file = str(Path(__file__).resolve().parent / 'conf.yaml')
conf_data = yaml.load(open(conf_file, 'r').read())

def request_url(name, url):
    try:
        r = requests.get(url, timeout=1)
        code = r.status_code
        r.close()
        return [name, code, time.strftime('%Y-%m-%d %H:%M:%S')]
    except Exception as e:
        return [name, 9, time.strftime('%Y-%m-%d %H:%M:%S')]

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

def set_redis(key, value):
    redis_conf = conf_data.get('redis_conf')
    redis_host = redis_conf.get('host')
    redis_port = redis_conf.get('port')
    redis_db = redis_conf.get('db')
    r = redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db,decode_responses=True)
    r.hmset(key, value)

def modeify_body(data):
    new_data = []
    status_info = ''
    for i in data:
        if i[1] == 200:
            status_code = 0
            status_info = 'ok'
        elif i[1] == 9:
            status_code = 9
            status_info = 'timeout'
        else:
            status_code = i[1]
            status_info = 'error'

        key = 'moniter:app_service:'+i[0]
        value = {
            'type': 'app_service',
            'name': i[0],
            'addr': app_service.get(i[0]),
            'status': status_code,
            'status_info': status_info,
            'last_check_time': i[2]
        }
        new_data.append([key, value])
    return new_data


app_service = conf_data.get('app_service')

data = task_run(app_service)
modeify_data = modeify_body(data)
for x in modeify_data:
    set_redis(x[0], x[1])
