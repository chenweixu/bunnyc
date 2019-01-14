#!/usr/bin/python
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2016-12-27 23:04:38
__author__ = "chenwx"

import pymysql


class Mysql_info(object):
    """docstring for Mysql_info
    mysql 的常用操作类
    """

    def __init__(self, ipaddr, user, passwd, dbname, port=3306, charset="utf8"):
        super(Mysql_info, self).__init__()
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
            txt = self.curs.fetchone()
            return txt
        except Exception as e:
            raise e

    def get_fetchall(self, sql):
        try:
            self.curs.execute(sql)
            txt = self.curs.fetchall()
            return txt
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
