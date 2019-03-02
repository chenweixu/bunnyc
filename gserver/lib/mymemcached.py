#!/usr/bin/python
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2016-12-29 01:12:15
__author__ = 'chenwx'

import time
from ipaddress import ip_address
from lib.memcached import Memcached


class my_memcached(Memcached):
    """docstring for my_memcached"""

    def __init__(self, ip, port):
        Memcached.__init__(self, ip, port)
        self.ip = ip
        self.port = port

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
