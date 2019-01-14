import threading
from lib.mylog import My_log
from lib.mymemcached import my_memcached
from lib.myredis import RedisQueue
from lib.conf import conf_data


class Get_memcache(threading.Thread):
    """获取 memcached 信息的线程
    """

    def __init__(self):
        super(Get_memcache, self).__init__()

    def run(self):
        work_log = My_log().get_log()
        work_log.debug("get memcached threading start")
        memcache_service_id = conf_data("memcache_id")
        r = RedisQueue(queuename="queue:bunnyc")
        for i in memcache_service_id.keys():
            work_log.debug("get memcache data work start : " + i)
            ip = memcache_service_id.get(i)[0]
            port = memcache_service_id.get(i)[1]
            work_log.debug(str(ip))
            try:
                mem_data = my_memcached(ip, port)
                work_log.debug("get memcache data success: " + i)
                data = mem_data.get_run_date(i)
                r.put(data)
                work_log.debug("memcache data put redis queue: " + i)
            except Exception as e:
                work_log.error("memcache data get error")
                work_log.error(str(e) + " : " + i)
        else:
            work_log.info("all memcache check end")
