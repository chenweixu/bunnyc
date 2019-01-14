#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2017-01-17 14:46:50
__author__ = 'chenwx'

from memcache import Client


class Memcached(object):
    """docstring for Memcached
    基础的 memcache 使用抽象类
    """

    def __init__(self, ip, port):
        super(Memcached, self).__init__()
        link = [str(ip) + ':' + str(port)]
        self.mc = Client(link, socket_timeout=1)

    def get_stats(self):
        status = self.mc.get_stats()
        if not status:
            raise Exception("linke memcache error")
        return status[0][1]

    def get_data(self, key):
        return self.mc.get(key)

    def set_data(self, key, value, time=10):
        return self.mc.set(key, value, time)
