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
from multiprocessing.dummy import Pool as ThreadPool

conf_file = str(Path(__file__).resolve().parent / "conf.yaml")
conf_data = yaml.load(open(conf_file, "r").read(), Loader=yaml.FullLoader)

def get_url(url):
    try:
        r = requests.get(url, timeout=2)
        code = r.status_code
        r.close()
        return code
    except Exception as e:
        return 9

def request_url(name, url):
    code = get_url(url)
    if code == 9:
        time.sleep(2)
        code = get_url(url)

    mess = {
        'name': name,
        'url': url,
        'status': code,
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

def set_redis(key, value):
    redis_conf = conf_data.get("redis")
    redis_host = redis_conf.get("host")
    redis_port = redis_conf.get("port")
    redis_db = redis_conf.get("queue_db")
    r = redis.StrictRedis(
        host=redis_host, port=redis_port, db=redis_db, decode_responses=True
    )
    r.rpush(key, value)


def run_task():
    web_service = conf_data.get("web_service")
    data = task_run(web_service)

    key = 'queue:bunnyc'
    new_data = {
        'mess_code': 2001,
        'type': 'web_service',
        'body': data,
        'ctime': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    set_redis(key, json.dumps(new_data))


def main():
    minute_1 = minute_5 = minute_10 = minute_30 = minute_60 = 0
    # 每1/5/10/30分钟进行一次的查询
    while 1:
        atime = int(time.time())
        if atime >= minute_1:
            minute_1 = atime + 60
            run_task()

        if atime >= minute_5:
            minute_5 = atime + 300

        if atime >= minute_10:
            minute_10 = atime + 600

        if atime >= minute_30:
            minute_30 = atime + 1800

        if atime >= minute_60:
            minute_60 = atime + 3600

        time.sleep(2)

if __name__ == '__main__':
    main()
