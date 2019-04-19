#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-25 13:46:42
__author__ = 'chenwx'

import sys
import json
import redis
import logging
from pathlib import Path
from lib.bunnycdb import Bunnyc_mysql
# from lib.mserver_data import MserverHost
from lib.mserver_data import MserverWebService
from lib.mserver_data import MserverMemcached
from lib.mserver_data import MserverTcpService
from lib.format_data import Format_data


class My_log(object):
    """docstring for My_log
    日志服务的基类
    """

    def __init__(self, log_file=None, level=logging.WARNING):
        super(My_log, self).__init__()

        self.logger = logging.getLogger()
        if not self.logger.handlers:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            typea = self.logger.setLevel(level)
            typea = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '[%(asctime)s]:%(filename)s:%(funcName)s:%(lineno)d :%(levelname)s: %(message)s'
            )
            typea.setFormatter(formatter)
            self.logger.addHandler(typea)

    def get_log(self):
        return self.logger


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

    def mysql_sessice(self):
        try:
            db_info = conf_data('bunnyc_mysql')
            host = db_info.get('host')
            port = db_info.get('port')
            user = db_info.get('user')
            passwd = db_info.get('passwd')
            dbname = db_info.get('dbname')

            work_mysql = Bunnyc_mysql(
                ipaddr=host,
                port=port,
                user=user,
                passwd=passwd,
                dbname=dbname
                )
            work_log.info('link mysql success')
        except Exception as e:
            work_log.error('link mysql db error')
            work_log.error(str(e))
            sys.exit(1)
        return work_mysql

    def task_linux_host_data(self,data,wredis,wmysql):
        # 先将原始的数据格式转换为规范的格式
        # 如果转换成功，则先插入 redis 再插入 mysql
        info = Format_data()
        try:
            new_data = info.format_host_data(data)
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
                wmysql.insert_host_linux_table(new_data)
                work_log.debug('linux data to mysql success')
            except Exception as e:
                work_log.error('linux data to mysql error')
                work_log.error(str(e))
                work_log.error(str(new_data))

    def task_web_service_data_format(self,data):
        body = data.get('body')
        work_log.debug(str(body))
        new_data = []
        status_info = ""

        for i in body:
            status = i.get('status')
            if status == 200:
                status = 0
                status_info = "ok"
            elif status == 9:
                status_info = "timeout"
            else:
                status_info = "error"

            key = "monitor:"+ str(data.get("mess_code")) + ":" + i.get('name')
            value = {
                "type": data.get("type"),
                "name": i.get('name'),
                "url": i.get('url'),
                "status": status,
                "status_info": status_info,
                "ctime": data.get("ctime")
            }
            new_data.append([key, value])
        return new_data

    def task_web_service(self, data, wredis):
        work_log.debug('task web_service run')
        try:
            new_data = self.task_web_service_data_format(data)
        except Exception as e:
            work_log.error('modeify web_service format error')
            work_log.error(str(e))
            new_data = False

        if new_data:
            for i in new_data:
                work_log.debug('------------------------')
                key = i[0]
                value = i[1]

                wredis.hmset(key, value)
                wredis.expire(key, 7200)
                work_log.debug('key: '+ str(key))
                work_log.debug('value: '+ str(value))

                # service_name = value.get('name')
                # service_status = value.get('status')

                # work_log.debug(str(fail_set))
                # work_log.debug(service_name+' : '+str(service_status))

                # if service_status == 0 and service_name not in fail_set:
                #     pass

                # elif service_status == 0 and service_name in fail_set:
                #     fail_set.remove(service_name)
                #     self.wredis.srem('fail:2001', service_name)
                #     self.wredis.sadd('restore:2001', service_name)
                #     self.work_log.info('redis srem fail:2001 | '+key)

                # elif service_status !=0 and service_name in fail_set:
                #     pass

                # elif service_status !=0 and service_name not in fail_set:
                #     fail_set.add(service_name)
                #     self.wredis.sadd('fail:2001', service_name)
                #     self.work_log.info('redis sadd fail:2001 | '+key)

    def task_memcache_data(self, data, wredis, wmysql):
        work_log.debug('task_memcache_data ------ start')
        work_log.debug('---------------------------------------')
        work_log.debug(str(data))
        work_log.debug('---------------------------------------')
        try:
            key = 'monitor:'+str(data.get('mess_code'))+':'+data.get('strid')
            wredis.hmset(key, data)
            wredis.expire(key, 7200)
            work_log.debug('memcached data to redis success')

            wmysql.insert_memcache_data(data)
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

                # if value == 0 and key not in fail_set:
                #     pass

                # elif value == 0 and key in fail_set:
                #     fail_set.remove(key)
                #     wredis.srem('fail:2010', key)
                #     wredis.sadd('restore:2010', key)
                #     work_log.info('redis srem fail:2010 | '+key)

                # elif value !=0 and key in fail_set:
                #     pass

                # elif value !=0 and key not in fail_set:
                #     fail_set.add(key)
                #     wredis.sadd('fail:2010', key)
                #     work_log.info('redis sadd fail:2010 | '+key)


    def run(self):

        '''从redis队列获取待处理的数据，处理完成后，
        分别存入redis和mysql mongodb
        '''
        work_log.info('mserver task thread start')
        redis_sessice = self.redis_sessice()
        mysql_sessice = self.mysql_sessice()

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
                    next_task = MserverMemcached(data, redis_sessice, mysql_sessice)
                    next_task.task_memcache_data()
                    self.task_memcache_data(data, redis_sessice)

                elif data_type == 'tcp_service':
                    next_task = MserverTcpService(data, redis_sessice)
                    next_task.run()
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
    work.start()

if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent

    logfile = work_dir / conf_data('mserver', 'log')
    log_revel = conf_data('bserver', 'log_revel')
    work_log = My_log(logfile, log_revel).get_log()
    main()
