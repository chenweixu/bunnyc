#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-25 13:46:42
__author__ = 'chenwx'

import sys
import json
from pathlib import Path
from lib.mylog import My_log
from lib.conf import conf_data
from lib.mserver_data import Mserver_task
from lib.myredis import RedisQueue
from lib.myredis import monitor_data
from lib.mymysql import Bunnyc_mysql


def mserver_work_task():
    '''从redis队列获取待处理的数据，处理完成后，
    分别存入redis和mysql mongodb
    '''
    work_log.info('mserver task thread start')
    redis_queue = RedisQueue(queuename='queue:bunnyc')
    redis_monitor_data = monitor_data()

    try:
        work_mysql = Bunnyc_mysql()
        work_log.info('link mysql success')
    except Exception as e:
        work_log.error('link mysql db error')
        work_log.error(str(e))
        sys.exit(1)

    while 1:
        data = json.loads(redis_queue.get())
        work_log.debug('mserver get cache success---------')
        work_log.debug(str(data))
        try:
            next_task = Mserver_task(data, redis_monitor_data, work_mysql)
            next_task.start()
        except Exception as e:
            work_log.error(str(e))
            work_log.error('Mserver_task mserver_run error')

def main():
    work_log.info('------admin start')
    mserver_work_task()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('mserver', 'log')
    work_log = My_log(logfile, conf_data('mserver', 'log_revel')).get_log()
    main()
