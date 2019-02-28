#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 23:31:29
__author__ = 'chenwx'

import redis
import requests
import yaml
import redis
import time
from pathlib import Path

conf_file = str(Path(__file__).resolve().parent / 'conf.yaml')
conf_data = yaml.load(open(conf_file, 'r').read())
sms_api = conf_data.get('sms_api')

def redis_link():
    redis_conf = conf_data.get('redis_conf')
    redis_host = redis_conf.get('host')
    redis_port = redis_conf.get('port')
    redis_db = redis_conf.get('db')
    r = redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db,decode_responses=True)
    return r

def get_moniter_app_service_error(redis_sessice):
    task = redis_sessice.keys(pattern='moniter:app_service:*')
    data = []
    for i in task:
        status = redis_sessice.hget(i, 'status')
        if status != 0:
            name = redis_sessice.hget(i, 'name')
            data.append([name, status])
    return data

def set_sms_mess(data):
    all_mess = []
    while len(data) > 0:
        mess = data[0:30]
        del data[0:30]
        new_data = ''
        for i in mess:
            new_data += ':'.join(i) + ' '
        all_mess.append('app_server error: '+ new_data.strip())
    return all_mess

def send_sms_mess(data):
    for i in data:
        print(i)
        mess = {"body": i, 'phone': conf_data.get('sms_phone')}
        print(mess)
        # r = requests.get(sms_api, params=mess, timeout=5)
        # code = r.status_code
        # r.close()

r = redis_link()
data = get_moniter_app_service_error(r)
mess = set_sms_mess(data)
send_sms_mess(mess)

