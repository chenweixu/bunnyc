#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 23:31:29
__author__ = 'chenwx'

import logging
import os
import redis
import requests
import yaml
import redis
import time
from pathlib import Path

# crontab: */10 * * * * /opt/app/bunnyc/alarm/alarm.py

conf_file = str(Path(__file__).resolve().parent / 'conf.yaml')
conf_data = yaml.load(open(conf_file, 'r').read())
sms_api = conf_data.get('sms_conf').get('sms_api')
alarm_conf = conf_data.get('alarm')

class My_log(object):
    """docstring for My_log
    日志服务的基类
    """

    def __init__(self, log_file=None, level=logging.WARNING):
        super(My_log, self).__init__()

        self.logger = logging.getLogger()
        if not self.logger.handlers:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            typea = self.logger.setLevel(level)
            typea = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                "[%(asctime)s]:%(filename)s:%(funcName)s:%(lineno)d :%(levelname)s: %(message)s"
            )
            typea.setFormatter(formatter)
            self.logger.addHandler(typea)

    def get_log(self):
        return self.logger

def redis_link():
    redis_conf = conf_data.get('redis')
    host = redis_conf.get('host')
    port = redis_conf.get('port')
    db = redis_conf.get('monitor_db')
    r = redis.StrictRedis(host=host,port=port,db=db,decode_responses=True)
    return r

def get_moniter_app_service_error(redis_sessice):
    task = redis_sessice.keys(pattern='moniter:2001:*')

    if not task:
        work_log.error('get redis key error: not data')
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
        mess = data[0:10]
        del data[0:10]
        new_data = ''
        for i in mess:
            new_data += ':'.join(i) + ' '
        all_mess.append('WebService检查故障: '+ new_data.strip())
    return all_mess

def send_sms_mess(data):
    mess = {"body": data, 'phone': conf_data.get('sms_conf').get('admin_phone')}
    work_log.info('send sms mess:')
    work_log.info(str(mess))
    # r = requests.get(sms_api, params=mess, timeout=5)
    # code = r.status_code
    # if code = 200:
    #     work_log.info('send sms sesscue')
    # r.close()

def run_web_service_task():
    r = redis_link()
    data = get_moniter_app_service_error(r)
    if not data:
        work_log.info('check web_service all success')
        return True
    mess = set_sms_mess(data)
    for i in mess:
        send_sms_mess(mess)


def main():
    minute_1 = minute_5 = minute_10 = minute_30 = minute_60 = 0
    # 每1/5/10/30分钟进行一次的查询
    while 1:
        atime = int(time.time())
        if atime >= minute_1:
            minute_1 = atime + 60
            run_web_service_task()

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
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / alarm_conf.get('log')
    work_log = My_log(logfile, alarm_conf.get('log_revel')).get_log()
    main()
