#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-22 14:18:53
__author__ = 'chenwx'
'''主要用于采集一些设备的信息
'''

import sys
import os
import time
import json
import socket
import threading
from pathlib import Path
from ipaddress import ip_address
from queue import Queue
import yaml
import redis
from pymemcache.client import Client
from lib.worklog import My_log
from lib.daemon import daemon
from lib.myconf import conf_data

class my_memcached(object):
    """docstring for my_memcached
    基础的 memcache 使用抽象类
    """

    def __init__(self, ip, port):
        super(my_memcached, self).__init__()
        # link = [str(ip) + ":" + str(port)]
        self.mc = Client((ip, int(port)),connect_timeout=2)
        self.ip = ip
        self.port = port

    def stats(self):
        return self.mc.stats()

    def show_stats(self, key):
        return self.stats().get(key.encode())

    def get_connections_sum(self):
        return int(self.stats().get("curr_connections".encode()))

    def get_mem_rate(self):
        data = self.stats()
        memsum = int(data.get("limit_maxbytes".encode()))
        memused = int(data.get("bytes".encode()))
        return round(memused / memsum * 100, 2)

    def get_run_date(self, strid):
        mem_data = self.stats()
        cmd_get = mem_data.get('cmd_get'.encode())
        get_hits = mem_data.get('get_hits'.encode())
        memsum = mem_data.get('limit_maxbytes'.encode())
        memused = mem_data.get('bytes'.encode())

        if cmd_get > 0:
            get_hits_rate = round(get_hits / cmd_get * 100, 2)
        else:
            get_hits_rate = 100

        run_data = {
            'mess_code': 1101,
            'mess_type': 102,
            'type': 'memcache',
            'strid': strid,
            'ip': self.ip,
            'intip': int(ip_address(self.ip)),
            'port': self.port,
            'memsum': memsum,
            'memused': memused,
            'cmd_get': cmd_get,
            'cmd_set': mem_data.get('cmd_set'.encode()),
            'get_hits': get_hits,
            'curr_connections': mem_data.get('curr_connections'.encode()),
            'total_connections': mem_data.get('total_connections'.encode()),
            'ram_used_rate': round(memused / memsum * 100, 2),
            'get_hits_rate': get_hits_rate,
            'ctime': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return run_data

class Get_memcache(threading.Thread):
    """获取 memcached 信息的线程
    """

    def __init__(self, queue):
        super(Get_memcache, self).__init__()
        self.queue = queue

    def run(self):
        work_log = My_log().get_log()
        work_log.debug("get memcached threading start")
        memcache_service_id = conf_data("memcache_id")
        for i in memcache_service_id.keys():
            work_log.debug("get memcache data work start : " + i)
            ip = memcache_service_id.get(i)[0]
            port = memcache_service_id.get(i)[1]
            work_log.debug('mc_ip: %s, mc_port: %d' % (ip, port))
            try:
                mem_data = my_memcached(ip, port)
                data = mem_data.get_run_date(i)
                self.queue.put(data)
                work_log.debug("memcache data put redis queue: " + i)
            except Exception as e:
                work_log.error("memcache data get error")
                work_log.error(str(e) + " : " + i)
        else:
            work_log.info("all memcache check end")

class SendBserver(threading.Thread):
    """docstring for SendBserver"""
    def __init__(self, queue):
        super(SendBserver, self).__init__()
        self.queue = queue

    def send_udp_mess(self, mess):
        # 通过 udp 发送数据
        # udp 是无状态的协议，没有发送失败这种情况，
        # server_addr = ('10.2.1.5', 8716)
        server_addr = tuple(conf_data('gserver', 'mess_server'))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(mess, server_addr)
            s.close()
        except socket.error:
            work_log.error('send_udp_mess socket.error')
        except Exception as e:
            work_log.error('send_udp_mess other error')
            work_log.error(str(e))

    def run(self):
        work_log = My_log().get_log()
        work_log.info('SendBserver thread start success')

        while 1:
            data = self.queue.get()
            work_log.debug('from queue get data success')
            work_log.debug(str(data))

            mess_code = data.get('mess_code')
            new_data = json.dumps(data).encode('utf-8')
            self.send_udp_mess(new_data)


def work_start():
    minute_1 = minute_5 = minute_10 = minute_30 = minute_60 = 0
    # 每1/5/10/30分钟进行一次的查询
    queue = Queue()
    mss_server = SendBserver(queue)
    mss_server.start()

    while 1:
        atime = int(time.time())
        if atime >= minute_1:
            minute_1 = atime + 60
            memcached_info = Get_memcache(queue)
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

    mss_server.join()

class work_daemon(daemon):
    """docstring for work_daemon"""
    def run(self):
        work_start()

def main():
    if len(sys.argv) == 2:
        daemon=work_daemon(pidfile)
        if 'start' == sys.argv[1]:
            work_log.info('------admin start daemon run ')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            work_log.info('------admin stop')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            work_log.info('------admin restart')
            daemon.restart()
        else:
            print('unkonow command')
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        work_log.info('------admin start')
        work_start()

if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('gserver', 'log')
    pidfile = work_dir / conf_data('gserver', 'pid')
    log_revel = conf_data('gserver', 'log_revel')
    work_log = My_log(logfile, log_revel).get_log()
    main()
