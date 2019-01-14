#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-22 14:18:53
__author__ = 'chenwx'
'''主要用于采集一些设备的信息
    memcache mysql
'''

import time
from pathlib import Path
from lib.mylog import My_log
from lib.conf import conf_data
from lib.get_memcache_thread import Get_memcache


def work_task():
    minute_1 = minute_5 = minute_10 = minute_30 = minute_60 = 0
    # 每1/5/10/30分钟进行一次的查询
    while 1:
        atime = int(time.time())
        if atime >= minute_1:
            minute_1 = atime + 60
            memcached_info = Get_memcache()
            memcached_info.start()

        if atime >= minute_5:
            minute_5 = atime + 300

        if atime >= minute_10:
            minute_10 = atime + 600

        if atime >= minute_30:
            minute_30 = atime + 1800

        if atime >= minute_60:
            minute_60 = atime + 3600

        time.sleep(2)


def main():
    work_log.info('------admin start')
    work_task()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('gserver', 'log')
    work_log = My_log(logfile, conf_data('gserver', 'log_revel')).get_log()
    main()
