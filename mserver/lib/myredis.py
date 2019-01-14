#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2017-02-08 03:13:15
__author__ = "chenwx"

import redis
from lib.conf import conf_data


class my_redis(object):
    """docstring for my_redis"""

    def __init__(self, dbname):
        super(my_redis, self).__init__()
        redis_conf = conf_data("redis")
        redis_host = redis_conf.get("host")
        redis_port = redis_conf.get("port")
        redis_db = redis_conf.get(dbname)
        self.r = redis.StrictRedis(
            host=redis_host, port=redis_port, db=redis_db, decode_responses=True
        )

    def link_redis(self, dbname="queue"):
        try:
            self.r.ping()
            return True
        except Exception:
            raise False


class set_test(my_redis):
    """docstring for set_test"""

    def __init__(self, dbname):
        my_redis.__init__(self, dbname)

    def set(self, key, vel):
        self.r.set(key, vel)

    def get(self, key):
        return self.r.get(key)


class RedisQueue(my_redis):
    def __init__(self, dbname="queue", queuename="queue:data"):
        my_redis.__init__(self, dbname)
        self.key = queuename

    def put(self, item):
        self.r.rpush(self.key, item)

    def get(self, timeout=None):
        item = self.r.blpop(self.key, timeout)
        if item:
            item = item[1]
        # return str(item,encoding="utf-8")
        return item

    def size(self):
        return self.r.llen(self.key)


class Get_data_db(my_redis):
    """docstring for Get_data_db"""

    def __init__(self, dbname="get_data"):
        my_redis.__init__(self, dbname)

    def wredis_get_data(self, data):
        data_type = data.get("type")
        strid = data.get("strid")
        key_name = strid + ":end"
        try:
            key_value = self.r.get(key_name)
            if not key_value:
                key_value = 0
                self.r.set(key_name, key_value)
            else:
                self.r.incr(key_name)
                key_value = int(key_value) + 1
            body_key = strid + ":" + str(key_value)
            self.r.hmset(body_key, data)
            if data_type != "ora_tbs":
                self.r.expire(body_key, 10800)  # 缓存时间 3 小时
            else:
                self.r.expire(body_key, 108000)  # 30h 必须大于 24 小时，不然统计不到日数据增长量
        except Exception as e:
            raise e


class monitor_data(my_redis):
    """docstring for Host_data_db"""

    def __init__(self, dbname="monitor_db"):
        my_redis.__init__(self, dbname)

    def wredis_monitor_data(self, data, timeout=7200):
        mess_code = data.get("mess_code")
        if mess_code:
            key_name = data.get("strid") + ":" + str(mess_code)
        else:
            key_name = data.get("strid")
        try:
            self.r.hmset(key_name, data)
            self.r.expire(key_name, timeout)  # redis_db 中保留时间 2 小时
        except Exception as e:
            raise e

    def redkey(self, key):
        try:
            return self.r.get(key)
        except Exception as e:
            raise e

    def set(self, key, value, timeout=10800):
        try:
            self.r.set(key, value)
            self.r.expire(key, timeout)
        except Exception as e:
            raise e

    def wredis_incr(self, key, timeout=600):
        try:
            self.r.incr(key)
            self.r.expire(key, timeout)
        except Exception as e:
            raise e

    def wredis_zero(self, key, timeout=600):
        try:
            self.r.set(key, 0)
            self.r.expire(key, timeout)
        except Exception as e:
            raise e
