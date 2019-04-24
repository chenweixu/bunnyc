#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2019-02-28 12:59:26
__author__ = "chenwx"

import telnetlib
import requests
import logging
import os
import yaml
import time
import json
import socket
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool


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
                "[%(asctime)s]:%(filename)s:%(funcName)s:%(lineno)d :%(levelname)s: %(message)s"
            )
            typea.setFormatter(formatter)
            self.logger.addHandler(typea)

    def get_log(self):
        return self.logger


class check_web_service(object):
    """docstring for check_web_service"""
    def __init__(self):
        super(check_web_service, self).__init__()

    def get_url(self, url):
        try:
            r = requests.get(url, timeout=2)
            code = r.status_code
            r.close()
            return code
        except Exception as e:
            return 9

    def request_url(self, name, url):
        code = self.get_url(url)
        if code == 9:
            time.sleep(2)
            code = self.get_url(url)
            if code == 9:
                work_log.info(f'web serice check: failure, timeoute, status: 9, {url}')

        mess = {
            'name': name,
            'url': url,
            'status': code,
        }
        return mess

    def task_run(self, url_list):
        pool = ThreadPool(50)
        result = []
        for name, url in url_list.items():
            result.append(pool.apply_async(self.request_url, (name, url)))
        pool.close()
        pool.join()

        Display = []
        for res in result:
            vle = res.get()
            if vle != 0:
                Display.append(vle)
        return Display

    def run_web_service_task(self):
        work_log.info('run_web_service_task -------- start')
        web_service = conf_data("web_service")
        data = self.task_run(web_service)

        new_data = {
            "mess_type": 102,
            'mess_code': 2001,
            'type': 'web_service',
            'body': data,
            'ctime': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        work_log.debug(str(new_data))
        send_mess_udp(new_data)
        work_log.debug('send data success')
        work_log.info('run_web_service_task -------- end')


class check_network_tcp(object):
    """docstring for check_network_tcp"""
    def __init__(self):
        super(check_network_tcp, self).__init__()

    def check_tcp_port(self, ip, port):
        try:
            tn = telnetlib.Telnet(ip, port=port, timeout=3)
            tn.close()
            # 检查正常
            work_log.debug("tcp check success, desc_host: %s ,port: %s" % (ip, str(port)))
            return 0
        except ConnectionRefusedError:
            # 主机通，端口不通
            # work_log.info("port_check error desc_host: %s ,port: %s: return status 1, ConnectionRefusedError" % (ip, str(port)))
            work_log.info(f"tcp port check failure,ip:{ip}, port:{port} host not linke, return status code 1, ConnectionRefusedError")
            return 1
        except Exception as e:
            # 其它原因，更多是对端主机和端口都不通
            # work_log.error("port_check error desc_host: %s ,port: %s: return status 9, other error" % (ip, str(port)))
            work_log.info(f"tcp port check failure,ip:{ip}, port:{port}, return status code 9, other error")
            work_log.info(str(e))
            return 9

    def port_check(self, ip_port):
        ip = ip_port.split(':')[0]
        port = ip_port.split(':')[1]
        code = self.check_tcp_port(ip, port)
        if code != 0:
            time.sleep(2)
            code = self.check_tcp_port(ip, port)
            if code != 0:
                work_log.info('check tcp_port 2 times timeoute, status: 9 '+str(ip_port))
        return [ip_port, code]

    def run_network_tcp_port_task(self):
        tcp_service = conf_data("network_tcp")
        work_log.info('run_network_tcp_port_task -------- start')
        mess = {}

        for service_name in tcp_service:
            pool = ThreadPool(30)
            result = []
            for addr in tcp_service.get(service_name):
                result.append(pool.apply_async(self.port_check, (addr,)))
            pool.close()
            pool.join()

            Display = []
            for res in result:
                vle = res.get()
                if vle != 0:
                    Display.append(vle)
            mess[service_name] = Display

        new_data = {
            "mess_type": 102,
            'mess_code': 2011,
            'type': 'tcp_service',
            'body': mess,
            'ctime': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        send_mess_udp(new_data)
        work_log.debug('send data success')
        work_log.debug(str(new_data))
        work_log.info('run_network_tcp_port_task -------- end')

def send_mess_udp(data):
    # 通过 udp 发送数据
    # udp 是无状态的协议，没有发送失败这种情况，
    mess = json.dumps(data).encode('utf-8')
    server_addr = tuple(conf_data('monitor', 'mess_server'))
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.sendto(mess, server_addr)
        s.close()
    except socket.error:
        work_log.error('udp socket error')
    except Exception as e:
        work_log.error('send data to udp socket error')
        work_log.error(str(e))

def conf_data(style, age=None):
    conf_file = work_dir / 'conf.yaml'
    data = yaml.load(conf_file.read_text(), Loader=yaml.FullLoader)
    if not age:
        return data.get(style)
    else:
        return data.get(style).get(age)

def main():
    second_20 = minute_1 = minute_5 = minute_10 = minute_30 = 0
    # 每1/5/10/30分钟进行一次的查询
    while 1:
        atime = int(time.time())

        if atime >= second_20:
            second_20 = atime + 20

        if atime >= minute_1:
            minute_1 = atime + 60
            try:
                web = check_web_service()
                web.run_web_service_task()
            except Exception as e:
                work_log.error('check_web_service error')
                work_log.error(str(e))

            try:
                tcp_service = check_network_tcp()
                tcp_service.run_network_tcp_port_task()
            except Exception as e:
                work_log.error('check_tcp_service error')
                work_log.error(str(e))

        if atime >= minute_5:
            minute_5 = atime + 300

        if atime >= minute_10:
            minute_10 = atime + 600

        if atime >= minute_30:
            minute_30 = atime + 1800

        time.sleep(2)

if __name__ == '__main__':
    work_dir = Path(__file__).resolve().parent
    logfile = work_dir / conf_data('monitor', 'log')
    work_log = My_log(logfile, conf_data('monitor', 'log_revel')).get_log()

    main()
