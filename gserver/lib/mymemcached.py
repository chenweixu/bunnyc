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
        mem_data = self.get_stats()

        run_data = {
            'type': 'memcache',
            'strid': strid,
            'ip': self.ip,
            'intip': int(ip_address(self.ip)),
            'port': self.port,
            'memsum': int(mem_data.get('limit_maxbytes')),
            'memused': int(mem_data.get('bytes')),
            'cmd_get': int(mem_data.get('cmd_get')),
            'cmd_set': int(mem_data.get('cmd_set')),
            'get_hits': int(mem_data.get('get_hits')),
            'curr_connections': int(mem_data.get('curr_connections')),
            'total_connections': int(mem_data.get('total_connections')),
            'ctime': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return run_data
