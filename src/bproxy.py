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
import sys
import time
import threading
import socket
import json
from pathlib import Path
from queue import Queue
import redis
import selectors
from lib.worklog import My_log
from lib.daemon import daemon
from lib.myconf import conf_data

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

class SelectorsTcpServer(object):
    '''监听TCP端口, 采用selectors 的IO复用实现，
        存在的问题：还没有对 TCP长报文 做应对,后续将进行解决'''

    def __init__(self, address, queue):
        self.queue = queue
        self.address = address
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 地址复用
        self.server.setblocking(False)
        # 非阻塞
        self.sel = selectors.DefaultSelector()

    def server_start(self):
        self.server.bind(self.address)
        self.server.listen(512)
        work_log.info(f'listen: {self.address}')
        self.sel.register(self.server, selectors.EVENT_READ, self.accept)

    def accept(self, server):
        conn, addr = server.accept()
        conn.setblocking(False)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn):
        data = conn.recv(2048)
        if data:
            client_ip = conn.getpeername()[0]
            work_log.debug(str(data))
            self.queue.put((data,client_ip))
            self.sel.unregister(conn)
            conn.close()
        else:
            self.sel.unregister(conn)
            conn.close()

    def monitor(self):
        work_log.info('SelectorsTcpServer - tcp select')
        while True:
            events_list = self.sel.select()
            for key, mask in events_list:
                callback = key.data
                callback(key.fileobj)

class SelectorsUcpServer(object):

    def __init__(self, address, queue):
        self.queue = queue
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.setblocking(False)
        self.server.bind(address)
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.server, selectors.EVENT_READ, self.read)

    def read(self, server):
        data, addr = server.recvfrom(4096)
        client_ip = addr[0]
        self.queue.put((data,client_ip))

    def monitor(self):
        work_log.info('SelectorsUcpServer - tcp select')
        while True:
            events_list = self.sel.select()
            for key, mask in events_list:
                callback = key.data
                callback(key.fileobj)

class DataToRedis(object):
    """docstring for Write_redis_queue
    用于从队列中取出数据，直接存入 redis 队列
    """
    def __init__(self, queue):
        super(DataToRedis, self).__init__()
        self.queue = queue

    def data_format(self, data, client_ip=None):
        try:
            try:
                info = json.loads(data.decode('utf-8'))
            except Exception as e:
                work_log.debug('data_format json error')
                work_log.debug(str(e))
                return

            if info.get('mess_type') == 101:
                info['ip'] = client_ip
                info['gtime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                return json.dumps(info)
                work_log.debug('mess_type 101 to queue')
            elif info.get('mess_type') == 102:
                return json.dumps(info)
                work_log.debug('mess_type 102 to queue')
            else:
                work_log.error(f'ip: {client_ip}, recv data mess_type error')

        except ValueError as e:
            work_log.error(f'ip: {client_ip}, ValueError: {str(e)}')
        except Exception as e:
            work_log.error(f'ip: {client_ip}, Exception: {str(e)}')

    def run(self):
        work_log.debug('Write_redis_queue thread start success')
        r = RedisQueue()
        work_log.debug('Write_redis_queue line redis success')

        while 1:
            data = self.queue.get()
            work_log.debug(str(data))
            try:
                r.put(self.data_format(data[0], data[1]))
                work_log.debug('write redis queue success')
            except Exception as e:
                work_log.error('write redis queue error')
                work_log.error(str(e))

class NetTcpThread(threading.Thread):
    def __init__(self, queue):
        super(NetTcpThread, self).__init__()
        self.queue = queue

    def run(self):
        """docstring for NetTcpThread"""
        listen_port = conf_data('bproxy', 'port')
        work_log.info('listen tcp thread start')

        try:
            task = SelectorsTcpServer(('0.0.0.0',8716), self.queue)
            task.server_start()
            task.monitor()
        except Exception as e:
            work_log.error('tcp thread error')
            work_log.error(str(e))

class NetUdpThread(threading.Thread):
    def __init__(self, queue):
        super(NetUdpThread, self).__init__()
        self.queue = queue

    def run(self):
        """docstring for NetUdpThread"""

        listen_port = conf_data('bproxy', 'port')
        address = ('', listen_port)
        work_log.info('listen udp thread start')
        try:
            task = SelectorsUcpServer(address, self.queue)
            task.monitor()
        except Exception as e:
            work_log.error('udp thread error')
            work_log.error(str(e))

class WriteRedisThread(threading.Thread):

    def __init__(self, queue):
        super(WriteRedisThread, self).__init__()
        self.queue = queue

    def run(self):
        try:
            work_log.debug('WriteRedisThread start')
            task = DataToRedis(self.queue)
            task.run()
        except Exception as e:
            work_log.error('WriteRedisThread error')
            work_log.error(str(e))

def work_start():
    work_log.info('------admin start')

    queue = Queue()

    listen_ucp = NetUdpThread(queue)
    listen_ucp.start()
    work_log.info('start udp server')

    listen_tcp = NetTcpThread(queue)
    listen_tcp.start()
    work_log.info('start tcp server')

    write_db = WriteRedisThread(queue)
    write_db.start()
    work_log.info('start wredis server')

    listen_ucp.join()
    listen_tcp.join()
    write_db.join()

class work_daemon(daemon):
    """docstring for work_daemon"""
    def run(self):
        work_start()

def main():
    if len(sys.argv) == 2:
        daemon=work_daemon(pidfile)
        if 'start' == sys.argv[1]:
            work_log.info('------admin start daemon run ')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            work_log.info('------admin stop')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            work_log.info('------admin restart')
            daemon.restart()
        else:
            print('unkonow command')
            sys.exit(2)
        sys.exit(0)
    elif len(sys.argv) == 1:
        work_start()


if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent

    logfile = work_dir / conf_data('bproxy', 'log')
    pidfile = work_dir / conf_data('bproxy', 'pid')
    log_revel = conf_data('bproxy', 'log_revel')
    work_log = My_log(logfile, log_revel).get_log()
    main()
