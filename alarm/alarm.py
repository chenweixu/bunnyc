#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 23:31:29
__author__ = "chenwx"

import logging
import os
import redis
import requests
import yaml
import time
from pathlib import Path

# crontab: */10 * * * * /opt/app/bunnyc/alarm/alarm.py

conf_file = str(Path(__file__).resolve().parent / "conf.yaml")
conf_data = yaml.load(open(conf_file, "r").read(), Loader=yaml.FullLoader)
sms_api = conf_data.get("sms_conf").get("sms_api")
alarm_conf = conf_data.get("alarm")


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
    redis_conf = conf_data.get("redis")
    host = redis_conf.get("host")
    port = redis_conf.get("port")
    r = redis.StrictRedis(host=host, port=port, decode_responses=True)
    return r

def set_sms_mess(data):
    all_mess = []
    while len(data) > 0:
        mess = data[0:10]
        del data[0:10]
        all_mess.append("WebService检查故障: " + " ".join(mess))
    return all_mess

def get_task_info(redis_sessice, task):
    data = []
    for i in task:
        work_log.debug('task: '+str(i))
        moniter_key = 'moniter:2001:'+i
        alarm_key = 'alarm:2001:'+i
        alarm_value = redis_sessice.get(alarm_key)
        if not alarm_value:
            work_log.debug(alarm_key+' not in redis')
            value = redis_sessice.hget(moniter_key, 'status')
            data.append(i+':'+str(value))
            redis_sessice.set(alarm_key, 0, ex=7200)
            work_log.debug(alarm_key+' set ex 7200')
        else:
            work_log.debug(alarm_key+ ' in redis, no add task')

    return data

def send_sms_mess(data):
    mess = {"body": data, "phone": conf_data.get("sms_conf").get("admin_phone")}
    work_log.info("send sms mess:")
    work_log.info(str(mess))
    # r = requests.get(sms_api, params=mess, timeout=5)
    # code = r.status_code
    # if code == 200:
    #     work_log.info("send sms sesscue")
    # r.close()


def run_web_service_task():
    r = redis_link()
    task = r.smembers('fail:2001')
    work_log.info('get fail:2001: '+str(task))
    if not task:
        work_log.info("check web_service all success")
        return True
    data = get_task_info(r, task)
    mess = set_sms_mess(data)
    for i in mess:
        send_sms_mess(i)


def main():
    minute_1 = minute_5 = minute_10 = 0
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

        time.sleep(2)


if __name__ == "__main__":
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / alarm_conf.get("log")
    work_log = My_log(logfile, alarm_conf.get("log_revel")).get_log()
    main()
