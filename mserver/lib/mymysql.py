#!/usr/bin/python
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2017-09-22 10:56:05
__author__ = 'chenwx'

import time
import datetime
from lib.mysql import Mysql_info
from lib.conf import conf_data


class Bunnyc_mysql(object):
    """docstring for Bunnyc_mysql"""

    def __init__(self):
        super(Bunnyc_mysql, self).__init__()
        db_info = conf_data('bunnyc_mysql')
        host = db_info.get('host')
        dbname = db_info.get('dbname')
        port = db_info.get('port')
        user = db_info.get('user')
        passwd = db_info.get('passwd')
        self.db_data = Mysql_info(
            ipaddr=host, user=user, passwd=passwd, dbname=dbname, port=port)

    def get_one_value(self, sql):
        try:
            info = self.db_data.get_fetchone(sql)
        except Exception as e:
            raise e
        return info

    def get_fetchone(self, sql):
        try:
            info = self.db_data.get_fetchone(sql)[0]
        except Exception as e:
            raise e
        return info

    def get_fetchall(self, sql):
        try:
            info = self.db_data.get_fetchall(sql)
        except Exception as e:
            raise e
        return info

    def insert_sql(self, sql):
        try:
            info = self.db_data.insert_sql(sql)
        except Exception as e:
            raise e
        return info

    def insert_sql_list(self, sql_list):
        try:
            self.db_data.insert_sql_list(sql_list)
        except Exception as e:
            raise e
        # return info

    def insert_host_linux_table(self, data):
        mess_code = data.get('mess_code')
        if mess_code == 1001:
            try:
                sql = "insert into t_host_cpu(\
                    ctime,ip,cpu,cpu_user_rate,cpu_nice_rate,cpu_system_rate,cpu_idle_rate,cpu_iowait_rate,cpu_irq_rate,cpu_softirq_rate,\
                    ld_1,ld_2,ld_3,proc_run,proc_sub) values (\
                    '%s','%s','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%d','%d')"  % (\
                    data.get('ctime'),
                    data.get('ip'),
                    data.get('cpu_rate'),
                    data.get('cpu_user_rate'),
                    data.get('cpu_nice_rate'),
                    data.get('cpu_system_rate'),
                    data.get('cpu_idle_rate'),
                    data.get('cpu_iowait_rate'),
                    data.get('cpu_irq_rate'),
                    data.get('cpu_softirq_rate'),
                    data.get('ld_1'),
                    data.get('ld_5'),
                    data.get('ld_15'),
                    data.get('proc_run'),
                    data.get('proc_sum')
                    )
            except Exception as e:
                raise e
            try:
                self.insert_sql(sql)
            except Exception as e:
                raise e

        elif mess_code == 1002:
            try:
                sql = "insert into t_host_ram(ctime,ip,mem,swap) values ('%s','%s','%d','%d')"  % (\
                    data.get('ctime'),
                    data.get('ip'),
                    data.get('mem_used_rate'),
                    data.get('swap_used_rate')
                    )
            except Exception as e:
                raise e
            try:
                self.insert_sql(sql)
            except Exception as e:
                raise e
        else:
            return 200


    def insert_memcache_data(self, data):
        try:
            sql = "insert t_memcached(\
                ctime,ip,mcid,mcport,memsum,memused,cmd_get,cmd_set,get_hits,curr_connections,total_connections) values (\
                '%s','%s','%d','%d','%d','%d','%d','%d','%d','%d','%d')" % (\
                data.get('ctime'),
                data.get('ip'),
                int(data.get('strid').strip('mc')),
                data.get('port'),
                data.get('memsum'),
                data.get('memused'),
                data.get('cmd_get'),
                data.get('cmd_set'),
                data.get('get_hits'),
                data.get('curr_connections'),
                data.get('total_connections'))
            self.insert_sql(sql)
        except Exception as e:
            raise e
