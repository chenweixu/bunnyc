# import json
# from lib.conf import conf_data
from lib.mylog import My_log
# from lib.resolve_host_data import resolve_host_data
from lib.resolve_host_data import Modify_data


class Mserver_Modify(object):
    """docstring for Mserver_Modify"""

    def __init__(self, data, wredis, mysql, redis_notice=None):
        super(Mserver_Modify, self).__init__()
        self.data = data
        self.wredis = wredis
        self.mysql = mysql
        self.redis_notice = redis_notice

        self.work_log = My_log().get_log()

    def __wredis_monitor_data(self, data):
        try:
            self.work_log.debug('__write redis work start')
            self.work_log.debug('---------------------------------------')
            self.work_log.debug(str(data))
            self.work_log.debug('---------------------------------------')
            self.work_log.debug('__write redis: ' + str(self.data.get('ip')))
            self.wredis.wredis_monitor_data(data)
            self.work_log.debug('__write redis success')
        except Exception as e:
            self.work_log.error('__write redis error')
            self.work_log.error(str(e))

    def __wmysql_data(self, data, iftype):
        self.work_log.debug('__wmysql_data work start: %s' % str(iftype))
        self.work_log.debug('__wmysql_data work ip: ' +
                            str(self.data.get('ip')))
        try:
            if iftype == 'host_linux':
                self.mysql.insert_host_linux_table(data)
            if iftype == 'memcache':
                self.mysql.insert_memcache_data(data)

            self.work_log.debug('__wmysql_data work success: %s' % str(iftype))
        except Exception as e:
            self.work_log.error('__wmysql_data run error')
            self.work_log.error(str(e))

    def task_linux_host_data(self):
        # 先将原始的数据格式转换为规范的格式
        # 如果转换成功，则先插入 redis 再插入 mysql
        try:
            ip = str(self.data.get('ip'))
            self.work_log.debug('modify data linux host = ' + ip)
            body = Modify_data()
            new_data = body.modify_linux_data(self.data)
            self.work_log.debug('modify data linux host = ' + ip +
                                ' ------ success')
        except Exception as e:
            self.work_log.error('modify data linux host error:' + ip)
            self.work_log.error(str(e))
            new_data = False

        if new_data:
            self.work_log.debug('task linux host new_data return success')
            self.__wredis_monitor_data(new_data)

            try:
                self.work_log.debug('write linux data to mysql work start: ' +
                                    ip)
                self.work_log.debug(str(new_data))
                self.__wmysql_data(new_data, iftype='host_linux')
                self.work_log.debug('write linux data to mysql success')
            except Exception as e:
                self.work_log.error('write mysql error ' + ip)
                self.work_log.error(str(e))
                self.work_log.debug(str(new_data))

    def task_memcache_data(self):
        # ip = self.data.get('ip')
        self.work_log.debug('task memcache data return success')
        self.__wredis_monitor_data(self.data)
        self.__wmysql_data(self.data, iftype='memcache')

    def start(self):
        self.work_log.debug('Mserver_Modify Mserver_Modify class start')
        try:
            data_type = self.data.get('type')
            if data_type == 'linux':
                self.task_linux_host_data()
            elif data_type == 'memcache':
                self.task_memcache_data()
            else:
                self.work_log.error('data_type unknown')
        except Exception as e:
            self.work_log.error('process data error')
            self.work_log.error(str(e))
