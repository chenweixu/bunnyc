#!/usr/bin/python
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2017-09-22 10:56:05
__author__ = 'chenwx'

import time
import datetime
import pymysql

class basemysql(object):
    """docstring for basemysql
    mysql 的常用操作基础类
    """

    def __init__(self, ipaddr, user, passwd, dbname, port=3306, charset="utf8"):
        super(basemysql, self).__init__()
        try:
            self.db_conn = pymysql.connect(
                host=ipaddr,
                port=port,
                user=user,
                passwd=passwd,
                db=dbname,
                charset=charset,
                connect_timeout=4,
            )
            self.curs = self.db_conn.cursor()
        except Exception as e:
            raise e

    def __del__(self):
        try:
            if hasattr(self, "curs"):
                self.curs.close()
            if hasattr(self, "db_conn"):
                self.db_conn.close()
        except Exception:
            pass

    def get_fetchone(self, sql):
        try:
            self.curs.execute(sql)
            data = self.curs.fetchone()
            return data
        except Exception as e:
            raise e

    def get_one_value(self, sql):
        try:
            info = self.get_fetchone(sql)[0]
        except Exception as e:
            raise e
        return info

    def get_fetchall(self, sql):
        try:
            self.curs.execute(sql)
            data = self.curs.fetchall()
            return data
        except Exception as e:
            raise e

    def insert_sql(self, sql):
        # 执行一条 SQL
        try:
            self.curs.execute(sql)
            self.db_conn.commit()
            return True
        except Exception as e:
            raise e

    def insert_sql_list(self, sql_list):
        # 连续插入多条 sql
        try:
            for i in sql_list:
                self.curs.execute(i)
            self.db_conn.commit()
        except Exception as e:
            raise e


class Bunnyc_mysql(basemysql):
    """docstring for Bunnyc_mysql"""

    def __init__(self,host,port,user,passwd,dbname):
        basemysql.__init__(self,
            ipaddr=host,
            user=user,
            passwd=passwd,
            dbname=dbname,
            port=port)

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
