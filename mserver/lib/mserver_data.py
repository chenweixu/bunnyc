import json
from lib.mylog import My_log
from lib.format_data import Format_data

class MserverHost(object):
    """docstring for MserverHost"""

    def __init__(self, data, wredis, mysql):
        super(MserverHost, self).__init__()
        self.data = data
        self.wredis = wredis
        self.mysql = mysql
        self.work_log = My_log().get_log()

    def task_linux_host_data(self):
        # 先将原始的数据格式转换为规范的格式
        # 如果转换成功，则先插入 redis 再插入 mysql
        info = Format_data()
        try:
            new_data = info.format_host_data(self.data)
            self.work_log.debug('format host data success: ' + str(self.data.get('mess_code')))
        except Exception as e:
            self.work_log.error('format host data error')
            self.work_log.error(str(e))
            self.work_log.error(str(self.data))
            self.work_log.error('--------------------')
            new_data = False

        if new_data:
            try:
                key = 'monitor:'+str(new_data.get('mess_code'))+':'+new_data.get('strid')
                self.wredis.hmset(key, new_data)
                self.wredis.expire(key, 7200)
                self.work_log.debug('linux data to redis success')
            except Exception as e:
                self.work_log.error('linux data to redis error')
                self.work_log.error(str(e))

            try:
                self.mysql.insert_host_linux_table(new_data)
                self.work_log.debug('linux data to mysql success')
            except Exception as e:
                self.work_log.error('linux data to mysql error')
                self.work_log.error(str(e))
                self.work_log.error(str(new_data))

class MserverWebService(object):
    """docstring for MserverWebService"""
    def __init__(self, data, wredis):
        super(MserverWebService, self).__init__()
        self.data = data
        self.wredis = wredis
        self.work_log = My_log().get_log()


    def modeify_web_service(self):
        body = self.data.get('body')
        self.work_log.debug(str(body))
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

            key = "monitor:"+ str(self.data.get("mess_code")) + ":" + i.get('name')
            value = {
                "type": self.data.get("type"),
                "name": i.get('name'),
                "url": i.get('url'),
                "status": status,
                "status_info": status_info,
                "ctime": self.data.get("ctime")
            }
            new_data.append([key, value])
        return new_data

    def task_web_service(self, fail_set):
        self.work_log.debug('task web_service run')
        try:
            new_data = self.modeify_web_service()
        except Exception as e:
            self.work_log.error('modeify web_service format error')
            self.work_log.error(str(e))
            new_data = False

        if new_data:
            for i in new_data:
                self.work_log.debug('------------------------')
                key = i[0]
                value = i[1]

                self.work_log.debug('key: '+ str(key))
                self.work_log.debug('value: '+ str(value))
                service_name = value.get('name')
                service_status = value.get('status')

                self.work_log.debug(str(fail_set))
                self.work_log.debug(service_name+' : '+str(service_status))

                if service_status == 0 and service_name not in fail_set:
                    pass

                elif service_status == 0 and service_name in fail_set:
                    fail_set.remove(service_name)
                    self.wredis.srem('fail:2001', service_name)
                    self.wredis.sadd('restore:2001', service_name)
                    self.work_log.info('redis srem fail:2001 | '+key)

                elif service_status !=0 and service_name in fail_set:
                    pass

                elif service_status !=0 and service_name not in fail_set:
                    fail_set.add(service_name)
                    self.wredis.sadd('fail:2001', service_name)
                    self.work_log.info('redis sadd fail:2001 | '+key)

                self.wredis.hmset(key, value)
                self.wredis.expire(key, 7200)

class MserverMemcached(object):
    """docstring for MserverMemcached"""
    def __init__(self, data, wredis, mysql):
        super(MserverMemcached, self).__init__()
        self.data = data
        self.wredis = wredis
        self.mysql = mysql
        self.work_log = My_log().get_log()

    def task_memcache_data(self):
        self.work_log.debug('task_memcache_data ------ start')
        self.work_log.debug('---------------------------------------')
        self.work_log.debug(str(self.data))
        self.work_log.debug('---------------------------------------')
        try:
            key = 'monitor:'+str(self.data.get('mess_code'))+':'+self.data.get('strid')
            self.wredis.hmset(key, self.data)
            self.wredis.expire(key, 7200)
            self.work_log.debug('memcached data to redis success')

            self.mysql.insert_memcache_data(self.data)
            self.work_log.debug('memcached data to mysql success')
        except Exception as e:
            self.work_log.error('memcached data to redis or mysql error')
            self.work_log.error(str(e))

class MserverTcpService(object):
    """docstring for MserverTcpService"""
    def __init__(self, data, wredis):
        super(MserverTcpService, self).__init__()
        self.data = data
        self.wredis = wredis
        self.work_log = My_log().get_log()

    def run(self, fail_set):
        self.work_log.debug('MserverTcpService start')
        body = self.data.get('body')
        mess_code = self.data.get('mess_code')
        for service_name, service_value in body.items():
            for i in service_value:
                key = i[0]
                value = i[1]
                rkey = "monitor:"+ str(mess_code) + ":" + key
                self.wredis.set(rkey, value, ex=7200)
                self.work_log.debug('TcpService data to redis success, key: %s' % rkey)

                if value == 0 and key not in fail_set:
                    pass

                elif value == 0 and key in fail_set:
                    fail_set.remove(key)
                    self.wredis.srem('fail:2010', key)
                    self.wredis.sadd('restore:2010', key)
                    self.work_log.info('redis srem fail:2010 | '+key)

                elif value !=0 and key in fail_set:
                    pass

                elif value !=0 and key not in fail_set:
                    fail_set.add(key)
                    self.wredis.sadd('fail:2010', key)
                    self.work_log.info('redis sadd fail:2010 | '+key)
