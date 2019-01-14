#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-22 13:44:24
# Version: 1.1.1
__author__ = 'chenwx'
'''
listen tcp and udp 8716 port
tcp thread 接收TCP协议数据，校验后传到队列
udp thread 接收UDP协议数据，校验后传到队列
wdb thread 从队列取数据，直接写入 redis 队列中
mess_type: 定义一个可以接收的数据包前提字段
'''

from pathlib import Path
from queue import Queue
from lib.mylog import My_log
from lib.conf import conf_data
from lib.bserver_tcp_thread import Net_tcp_server
from lib.bserver_udp_thread import Net_udp_server
from lib.bserver_write_queue import Write_redis_queue


def main():
    work_log.info('------admin start')

    queue = Queue()

    listen_ucp = Net_udp_server(queue)
    listen_ucp.start()
    work_log.info('start udp server')

    listen_tcp = Net_tcp_server(queue)
    listen_tcp.start()
    work_log.info('start tcp server')

    write_db = Write_redis_queue(queue)
    write_db.start()
    work_log.info('start wredis server')

    listen_ucp.join()
    listen_tcp.join()
    write_db.join()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('bserver', 'log')
    work_log = My_log(logfile, conf_data('bserver', 'log_revel')).get_log()
    main()
