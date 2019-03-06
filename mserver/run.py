#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-25 13:46:42
__author__ = 'chenwx'

import sys
import json
import redis
from pathlib import Path
from lib.mylog import My_log
from lib.conf import conf_data
from lib.mymysql import Bunnyc_mysql
from lib.mserver_data import MserverHost
from lib.mserver_data import MserverWebService
from lib.mserver_data import MserverMemcached


def mserver_work_task():
    '''从redis队列获取待处理的数据，处理完成后，
    分别存入redis和mysql mongodb
    '''
    work_log.info('mserver task thread start')
    redis_conf = conf_data("redis")
    redis_sessice = redis.Redis(
        host=redis_conf.get("host"),
        port=redis_conf.get("port"),
        db=redis_conf.get("queue"),
        decode_responses=True
        )

    try:
        work_mysql = Bunnyc_mysql()
        work_log.info('link mysql success')
    except Exception as e:
        work_log.error('link mysql db error')
        work_log.error(str(e))
        sys.exit(1)

    fail_2001 = []

    while 1:
        data = json.loads(redis_sessice.blpop("queue:bunnyc")[1])
        work_log.debug('mserver blpop redis cache success---------')
        work_log.debug(str(data))

        try:
            data_type = data.get('type')
            if data_type == 'linux':
                next_task = MserverHost(data, redis_sessice, work_mysql)
                next_task.task_linux_host_data()

            elif data_type == 'web_service':
                next_task = MserverWebService(data, redis_sessice)
                next_task.task_web_service(fail_list=fail_2001)

            elif data_type == 'memcache':
                next_task = MserverMemcached(data, redis_sessice, work_mysql)
                next_task.task_memcache_data()

        except Exception as e:
            work_log.error('mserver_work_task run error')
            work_log.error(str(e))

def main():
    work_log.info('------admin start')
    mserver_work_task()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('mserver', 'log')
    work_log = My_log(logfile, conf_data('mserver', 'log_revel')).get_log()
    main()
