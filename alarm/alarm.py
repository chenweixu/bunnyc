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

conf_file = str(Path(__file__).resolve().parent / "conf.yaml")
conf_data = yaml.load(open(conf_file, "r").read(), Loader=yaml.FullLoader)
sms_api = conf_data.get("sms_conf").get("api")
app_conf = conf_data.get("alarm")


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


class check_web_service(object):
    """docstring for check_web_service"""

    def __init__(self):
        super(check_web_service, self).__init__()

    def get_task_info(self, redis_sessice, task):
        data = []
        for i in task:
            monitor_key = "monitor:2001:" + i
            alarm_key = "alarm:2001:" + i
            alarm_value = redis_sessice.get(alarm_key)
            if not alarm_value:
                work_log.debug(alarm_key + " not in redis")
                value = redis_sessice.hget(monitor_key, "status")
                data.append(i + ":" + str(value))
                redis_sessice.set(alarm_key, 0, ex=7200)
                work_log.debug(alarm_key + " set ex 7200")
            else:
                work_log.debug(alarm_key + " in redis, no add task")
        return data

    def start(self):
        r = redis_link()
        task = r.smembers("fail:2001")
        restore = r.smembers("restore:2001")
        work_log.debug("--------------------")
        work_log.info("get fail:2001: " + str(task))
        if not task and not restore:
            # 没有故障信息和恢复信息
            work_log.info("check web_service all success")
            return True

        if task:
            try:
                data = self.get_task_info(r, task)
                mess = set_sms_mess("WebService检查故障: ", data)
                for i in mess:
                    send_sms_mess(i)
            except Exception as e:
                work_log.error('operating fail task error')
                work_log.error(str(e))

        if restore:
            try:
                mess = set_sms_mess("WebService检查恢复: ", list(restore))
                for i in mess:
                    send_sms_mess(i)
                for i in restore:
                    alarm_key = "alarm:2001:" + i
                    r.delete(alarm_key)         # 删除已告警状态
                    work_log.info('service restore: %s, delete redus alarm_key: %s' % (i, alarm_key))
                r.delete("restore:2001")        # 删除恢复任务队列集合
            except Exception as e:
                work_log.error('operating restore task error')
                work_log.error(str(e))


class Check_Tcp_Service(object):
    """docstring for Check_Tcp_Service"""
    def __init__(self):
        super(Check_Tcp_Service, self).__init__()

    def fail_task(self, redis_sessice, data):
        new_data = []
        for i in data:
            alarm_key = "alarm:2010:" + i
            alarm_value = redis_sessice.get(alarm_key)
            if not alarm_value:
                work_log.debug(alarm_key + " not in redis")
                new_data.append(i)
                redis_sessice.set(alarm_key, 0, ex=7200)
            else:
                work_log.debug(alarm_key + " in redis, no add task")
        return new_data

    def start(self):
        r = redis_link()

        fail_list = r.smembers("fail:2010")
        restore_list = r.smembers("restore:2010")

        work_log.info("get fail:2010: " + str(fail_list))
        work_log.info("get restore:2010: " + str(restore_list))

        if not fail_list and not restore_list:
            # 没有故障信息和恢复信息
            work_log.info("check tcp_service all success")
            return True

        if fail_list:
            try:
                data = self.fail_task(r, fail_list)
                mess = set_sms_mess("TCP服务检查故障: ", data)
                for i in mess:
                    send_sms_mess(i)
            except Exception as e:
                work_log.error('operating fail task error')
                work_log.error(str(e))

        if restore_list:
            try:
                mess = set_sms_mess("TCP服务检查恢复: ", list(restore_list))
                for i in mess:
                    send_sms_mess(i)
                for i in restore_list:
                    alarm_key = "alarm:2010:" + i
                    r.delete(alarm_key)         # 删除已告警状态
                    work_log.info('service restore: %s, delete redus alarm_key: %s' % (i, alarm_key))
                r.delete("restore:2010")        # 删除恢复任务队列集合
            except Exception as e:
                work_log.error('operating restore task error')
                work_log.error(str(e))


def redis_link():
    redis_conf = conf_data.get("redis")
    host = redis_conf.get("host")
    port = redis_conf.get("port")
    r = redis.StrictRedis(host=host, port=port, decode_responses=True)
    return r


def set_sms_mess(head_mess, data):
    all_mess = []
    while len(data) > 0:
        mess = data[0:20]
        del data[0:20]
        all_mess.append(head_mess + " ".join(mess))
    return all_mess


def send_sms_mess(data):
    mess = {"body": data, "phone": conf_data.get("sms_conf").get("admin_phone")}
    work_log.info("send sms mess:")
    work_log.info(str(mess))
    try:
        r = requests.get(sms_api, params=mess, timeout=5)
        code = r.status_code
        if code == 200:
            work_log.info("send sms sesscue")
        r.close()
    except Exception as e:
        work_log.error("request sms api error")
        work_log.error(str(e))


def main():
    second_20 = minute_1 = minute_5 = minute_10 = 0
    # 每1/5/10/30分钟进行一次的查询
    while 1:
        atime = int(time.time())

        if atime >= second_20:
            second_20 = atime + 20
            web_service = check_web_service()
            web_service.start()

            tcp_service = Check_Tcp_Service()
            tcp_service.start()

        if atime >= minute_1:
            minute_1 = atime + 60

        if atime >= minute_5:
            minute_5 = atime + 300

        if atime >= minute_10:
            minute_10 = atime + 600

        time.sleep(2)


if __name__ == "__main__":
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / app_conf.get("log")
    work_log = My_log(logfile, app_conf.get("log_revel")).get_log()
    main()
