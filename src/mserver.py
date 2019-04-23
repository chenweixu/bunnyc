#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-25 13:46:42
__author__ = 'chenwx'

import sys
import json
import redis
import re
import yaml
from pathlib import Path
from lib.format_data import Format_data
from lib.worklog import My_log
from lib.bunnycDB import BunnycDB


class Work_task(object):
    """docstring for Work_task"""
    def __init__(self):
        super(Work_task, self).__init__()

    def redis_sessice(self):
        redis_conf = conf_data("redis")
        redis_line = redis.Redis(
            host=redis_conf.get("host"),
            port=redis_conf.get("port"),
            db=redis_conf.get("queue"),
            decode_responses=True
            )
        return redis_line

    def task_linux_host_data(self,data,wredis,wmysql):
        # 先将原始的数据格式转换为规范的格式
        # 如果转换成功，则先插入 redis 再插入 mysql
        host_to_as = conf_data('host_to_as')
        info = Format_data()
        try:
            new_data = info.format_host_data(data, host_to_as)
            work_log.debug('format host data success: ' + str(data.get('mess_code')))
        except Exception as e:
            work_log.error('format host data error')
            work_log.error(str(e))
            work_log.error(str(data))
            work_log.error('--------------------')
            new_data = False

        if new_data:
            try:
                key = 'monitor:'+str(new_data.get('mess_code'))+':'+new_data.get('strid')
                wredis.hmset(key, new_data)
                wredis.expire(key, 7200)
                work_log.debug('linux data to redis success')
            except Exception as e:
                work_log.error('linux data to redis error')
                work_log.error(str(e))

            try:
                mess_code = new_data.get('mess_code')
                if mess_code == 1001:
                    wmysql.inster_t_host_cpu(new_data)
                    work_log.debug('linux data 1001 to mysql success')
                elif mess_code == 1002:
                    wmysql.inster_t_host_ram(new_data)
                    work_log.debug('linux data 1002 to mysql success')
                else:
                    work_log.error('wmysql: ignore mess_code')
            except Exception as e:
                work_log.error('linux data to mysql error')
                work_log.error(str(e))
                work_log.error(str(new_data))

    def task_web_service(self, data, wredis):
        work_log.debug('task web_service run')
        work_log.debug(str(data))
        try:
            info = Format_data()
            new_data = info.format_webService_data(data)
        except Exception as e:
            work_log.error('modeify web_service format error')
            work_log.error(str(e))
            new_data = False

        if new_data:
            for i in new_data:
                work_log.debug('--------web service data to redis---------')
                key = i[0]
                value = i[1]

                wredis.hmset(key, value)
                wredis.expire(key, 7200)
                work_log.debug('key: '+ str(key))
                work_log.debug('value: '+ str(value))

    def task_memcache_data(self, data, wredis, wmysql):
        work_log.debug('task_memcache_data ------ start')
        work_log.debug('---------------------------------------')
        work_log.debug(str(data))
        work_log.debug('---------------------------------------')
        try:
            key = 'monitor:'+str(data.get('mess_code'))+':'+data.get('strid')
            wredis.hmset(key, data)
            wredis.expire(key, 7200)
            wmysql.inster_t_memcached(data)
            work_log.debug('memcached data to mysql success')
        except Exception as e:
            work_log.error('memcached data to redis or mysql error')
            work_log.error(str(e))

    def task_tcp_service(self, data, wredis):
        work_log.debug('MserverTcpService start')
        body = data.get('body')
        mess_code = data.get('mess_code')
        for service_name, service_value in body.items():
            for i in service_value:
                key = i[0]
                value = i[1]
                rkey = "monitor:"+ str(mess_code) + ":" + key
                wredis.set(rkey, value, ex=7200)
                work_log.debug('TcpService data to redis success, key: %s' % rkey)

    def get_bunnyc_dblink(self):
        db_info = conf_data('bunnyc_mysql')
        dbhost = db_info.get('host')
        port = db_info.get('port')
        dbuser = db_info.get('user')
        dbpasswd = db_info.get('passwd')
        dbname = db_info.get('dbname')

        dblink = f'mysql+pymysql://{dbuser}:{dbpasswd}@{dbhost}:{port}/{dbname}'
        return dblink

    def run(self):

        '''从redis队列获取待处理的数据，处理完成后，
        分别存入redis和mysql mongodb
        '''
        work_log.info('mserver task thread start')
        redis_sessice = self.redis_sessice()
        mysql_sessice = BunnycDB(self.get_bunnyc_dblink())

        while 1:
            data = json.loads(redis_sessice.blpop("queue:bunnyc")[1])
            work_log.debug('mserver blpop redis cache success---------')
            work_log.debug(str(data))

            try:
                data_type = data.get('type')
                if data_type == 'linux':
                    self.task_linux_host_data(data,redis_sessice, mysql_sessice)

                elif data_type == 'web_service':
                    self.task_web_service(data, redis_sessice)

                elif data_type == 'memcache':
                    self.task_memcache_data(data, redis_sessice, mysql_sessice)

                elif data_type == 'tcp_service':
                    self.task_tcp_service(data, redis_sessice)

            except Exception as e:
                work_log.error('mserver_work_task run error')
                work_log.error(str(e))

def conf_data(style, age=None):
    conf_file = work_dir / 'conf.yaml'
    data = yaml.load(conf_file.read_text(), Loader=yaml.FullLoader)
    if not age:
        return data.get(style)
    else:
        return data.get(style).get(age)

def main():
    work_log.info('------admin start')
    work = Work_task()
    work.run()

if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent

    logfile = work_dir / conf_data('mserver', 'log')
    log_revel = conf_data('mserver', 'log_revel')
    work_log = My_log(logfile, log_revel).get_log()
    main()
