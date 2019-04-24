#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-22 13:44:24
# Version: 1.1.2
__author__ = 'chenwx'
'''
listen tcp and udp 8716 port
tcp thread 接收TCP协议数据，校验后传到队列
udp thread 接收UDP协议数据，校验后传到队列
wdb thread 从队列取数据，直接写入 redis 队列中
mess_type: 定义一个可以接收的数据包前提字段
'''
import os
import time
import logging
import threading
import socket
import json
from pathlib import Path
from queue import Queue
import yaml
import redis

class RedisQueue(object):
    """docstring for RedisQueue"""
    def __init__(self):
        super(RedisQueue, self).__init__()
        redis_conf = conf_data('redis')
        redis_host = redis_conf.get('host')
        redis_port = redis_conf.get('port')
        redis_db = redis_conf.get('queue')
        self.r = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True)
        self.queue = 'queue:bunnyc'

    def put(self, item):
        self.r.rpush(self.queue, item)

    def get(self, timeout=None):
        item = self.r.blpop(self.queue, timeout)
        if item:
            item = item[1]
        # return str(item,encoding="utf-8")
        return item

    def size(self):
        return self.r.llen(self.queue)


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


class Net_tcp_server(threading.Thread):
    def __init__(self, queue):
        super(Net_tcp_server, self).__init__()
        self.queue = queue

    def run(self):
        """docstring for Net_tcp_server
        监听TCP接口的线程，不符合接收规则就丢弃；
        符合则添加上IP和时间字段，再传入待处理队列中
        存在的问题：还没有对 TCP长报文 做应对,后续将进行解决
        """
        listen_port = conf_data('bproxy', 'port')

        work_log.info('listen tcp thread start')

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(('', listen_port))
            server.listen(5)
            work_log.info('bind tcp listen_port success')
        except Exception as e:
            work_log.error('listen tcp port error')
            work_log.error(str(e))

        while True:
            connection, client_addr = server.accept()
            client_ip = client_addr[0]
            data = connection.recv(4096)
            connection.close()
            work_log.debug('input tcp data from ip: ' + client_ip)
            try:
                try:
                    info = json.loads(data.decode('utf-8'))
                except Exception as e:
                    continue

                if info.get('mess_type') == 101:
                    info['ip'] = client_ip
                    info['gtime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.queue.put(info)
                    work_log.debug('send tcp data to queue success: ' +
                                   client_ip)
                elif info.get('mess_type') == 102:
                    self.queue.put(info)
                    work_log.debug('mess_type 102 to queue')
                else:
                    work_log.error(client_ip + ',' + 'mess_type error')
            except ValueError as e:
                work_log.info(client_ip + ': ' + str(e))
                work_log.info('not data')
            except Exception as e:
                work_log.error(client_ip + ': ' + str(e))
        server.close()


class Net_udp_server(threading.Thread):
    def __init__(self, queue):
        super(Net_udp_server, self).__init__()
        self.queue = queue

    def run(self):
        """docstring for Net_udp_server
        监听UDP接口的线程，不符合接收规则就丢弃；
        符合则添加上IP和时间字段，再传入待处理队列中
        存在的问题：没有对 udp长报文 做应对，这个有点麻烦，决定短消息用UDP，长消息用TCP
        """

        listen_port = conf_data('bproxy', 'port')

        work_log.info('listen udp thread start')
        try:
            address = ('', listen_port)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(address)
        except Exception as e:
            work_log.error('listen udp port error')
            work_log.error(str(e))

        while True:
            data, addr = s.recvfrom(4096)
            work_log.debug('input udp data from ip: ' + addr[0])
            try:
                try:
                    info = json.loads(data.decode('utf-8'))
                except Exception:
                    continue

                if info.get('mess_type') == 101:
                    info['ip'] = addr[0]
                    info['gtime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.queue.put(info)
                    work_log.debug('send udp date to queue success: ' +
                                   addr[0])
                    work_log.debug('Net_udp_server mess_code: ' +
                                   str(info.get('mess_code')))
                elif info.get('mess_type') == 102:
                    self.queue.put(info)
                    work_log.debug('mess_type 102 to queue')
                else:
                    work_log.debug(str(info))
                    work_log.error(addr[0] + ',' + 'mess_type error')
            except ValueError as e:
                work_log.error(addr[0] + ': ' + str(e))
            except Exception as e:
                work_log.error(addr[0] + ': ' + str(e))
        s.close()


class Write_redis_queue(threading.Thread):
    """docstring for Write_redis_queue
    用于从队列中取出数据，直接存入 redis 队列
    """

    def __init__(self, queue):
        super(Write_redis_queue, self).__init__()
        self.queue = queue

    def run(self):
        work_log = My_log().get_log()
        work_log.debug('Write_redis_queue thread start success')
        r = RedisQueue()
        work_log.debug('Write_redis_queue line redis success')

        while 1:
            data = self.queue.get()
            try:
                r.put(json.dumps(data))
                work_log.debug('write redis queue success')
            except Exception as e:
                work_log.error('write redis queue error')
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

    queue = Queue()

    listen_ucp = Net_udp_server(queue)
    listen_ucp.start()
    work_log.info('start udp server')

    listen_tcp = Net_tcp_server(queue)
    listen_tcp.start()
    work_log.info('start tcp server')

    write_db = Write_redis_queue(queue)
    write_db.start()
    work_log.info('start wredis server')

    listen_ucp.join()
    listen_tcp.join()
    write_db.join()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent

    logfile = work_dir / conf_data('bproxy', 'log')
    log_revel = conf_data('bproxy', 'log_revel')
    work_log = My_log(logfile, log_revel).get_log()
    main()
