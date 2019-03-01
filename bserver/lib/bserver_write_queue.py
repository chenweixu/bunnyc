import threading
import json
from lib.mylog import My_log
from lib.myredis import RedisQueue


class Write_redis_queue(threading.Thread):
    """docstring for Write_redis_queue
    用于从队列中取出数据，直接存入 redis 队列
    """

    def __init__(self, queue):
        super(Write_redis_queue, self).__init__()
        self.queue = queue

    def run(self):
        work_log = My_log().get_log()
        work_log.info('Write_redis_queue thread start success')

        while 1:
            data = self.queue.get()
            # print(json.dumps(data))
            # print(type())
            work_log.debug('from queue get data success')
            work_log.debug(str(data))
            ip = data.get('ip')

            try:
                work_log.debug('write redis queue: ' + ip)
                r = RedisQueue(queuename='queue:bunnyc')
                r.put(json.dumps(data))
                work_log.debug('write redis queue success: ' + ip)
            except Exception as e:
                work_log.error('write redis queue error: ' + ip)
                work_log.error(str(e))
