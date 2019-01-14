#!/usr/bin/python
# -*- coding: utf-8 -*-
# Email: chenwx716@163.com
# DateTime: 2018-07-23 14:11:08

# version: 1.1.1
__author__ = 'chenwx'

import socket
import time
import os
import sys
import commands
import re
import platform
import json
from signal import SIGTERM

server_addr = ('10.27.10.181', 8716)

tcp_protocol = True  # True | False
debug = False  # True | False


class Base_str_task(object):
    """docstring for Base_str_task"""

    def __init__(self):
        super(Base_str_task, self).__init__()

    def strlist_to_intlist(self, list_str):
        # 字符型列表转int 型列表
        x = []
        for i in list_str:
            if i.isdigit():
                x.append(int(i))
            else:
                x.append(i)
        return x


class Local_info(Base_str_task):
    """docstring for Local_info
        采集主机信息，
        部分数据是本地组装为字典，部分为采集原始数据，发送到服务器端解析
    """

    def __init__(self):
        super(Local_info, self).__init__()

    def get_cpu_stat_data(self, times=3):
        # 两次间隔采集 /proc/stst 文件的信息
        a = self.strlist_to_intlist(open('/proc/stat').readline().split()[1:])
        time.sleep(times)
        b = self.strlist_to_intlist(open('/proc/stat').readline().split()[1:])
        return (a, b)

    def get_meminfo(self):
        # 将 meminfo 文件内容转为一个字典
        data = open("/proc/meminfo", "r").readlines()
        meminfo = {}
        for i in data:
            key = re.findall(r'.*:', i)[0].strip(':')
            val = int(re.findall(r'\b[0-9]+', i)[0])
            meminfo[key] = val
        return meminfo

    def get_loadavg(self):
        # 包含有负载信息和当前任务数信息
        load = open('/proc/loadavg', 'r').readline().split()
        return load

    def get_disk_data(self):
        # 磁盘的空间使用率
        data = commands.getstatusoutput('/bin/df -P -x tmpfs')[1]
        disk = []
        f = data.split('\n')
        for i in f[1:]:
            disk.append(self.strlist_to_intlist(i.split()))
        return disk

    def get_disk_io(self):
        # 磁盘 io 信息采集
        data = commands.getstatusoutput('iostat')[1]
        disk_a = data.split('\n')[6:]
        disk_io_tuple = []
        for i in disk_a:
            if i:
                disk_io_tuple.append(i.split())
        return disk_io_tuple


class Network_linux_info(Base_str_task):
    """docstring for Network_linux_info
        网络状态信息采集
    """

    def __init__(self):
        super(Network_linux_info, self).__init__()

    def get_tcp_link_status(self):
        # TCP 协议的各种状态
        data = open('/proc/net/tcp', 'r').readlines()
        status = []
        for i in data:
            line = i.split()
            status.append(line[3])
        new_data = {
            'ERROR_STATUS': len([i for i in status if i == '00']),
            'TCP_ESTABLISHED': len([i for i in status if i == '01']),
            'TCP_SYN_SENT': len([i for i in status if i == '02']),
            'TCP_SYN_RECV': len([i for i in status if i == '03']),
            'TCP_FIN_WAIT1': len([i for i in status if i == '04']),
            'TCP_FIN_WAIT2': len([i for i in status if i == '05']),
            'TCP_TIME_WAIT': len([i for i in status if i == '06']),
            'TCP_CLOSE': len([i for i in status if i == '07']),
            'TCP_CLOSE_WAIT': len([i for i in status if i == '08']),
            'TCP_LAST_ACK': len([i for i in status if i == '09']),
            'TCP_LISTEN': len([i for i in status if i == '0A']),
            'TCP_CLOSING': len([i for i in status if i == '0B'])
        }
        return new_data

    def get_socket_status(self):
        # sockstat 状态信息
        data = open('/proc/net/sockstat', 'r').readlines()
        new_data = []
        for i in data:
            new_data.append(i.strip('\n'))
        return new_data

    def get_network_interface_info(self):
        # 采集流量信息，和丢包、错包状态
        data = open('/proc/net/dev', 'r').readlines()
        a = []
        for i in data[2:]:
            a.append(self.strlist_to_intlist(i.replace(':', ' ').split()))
        return a

    def get_network_ss_status(self):
        # 通过 ss 命令采集 socket 的状态
        data = commands.getstatusoutput('/usr/sbin/ss -s')[1].split('\n')
        new_data = {
            'total': int(re.findall(r'\d+', data[0])[0]),
            'kernel': int(re.findall(r'\d+', data[0])[1]),
            'tcp': {
                'tcp': int(re.findall(r'\d+', data[1])[0]),
                'estab': int(re.findall(r'\d+', data[1])[1]),
                'closed': int(re.findall(r'\d+', data[1])[2]),
                'orphaned': int(re.findall(r'\d+', data[1])[3]),
                'synrecv': int(re.findall(r'\d+', data[1])[4]),
                'timewait1': int(re.findall(r'\d+', data[1])[5]),
                'timewait2': int(re.findall(r'\d+', data[1])[6]),
                'ports': int(re.findall(r'\d+', data[1])[7])
            },
            'ss_x': {
                'total': int(re.findall(r'\d+', data[4])[0])
            },
            'RAW': {
                'total': int(re.findall(r'\d+', data[5])[0]),
                'ip': int(re.findall(r'\d+', data[5])[1]),
                'ipv6': int(re.findall(r'\d+', data[5])[2])
            },
            'UDP': {
                'total': int(re.findall(r'\d+', data[6])[0]),
                'ip': int(re.findall(r'\d+', data[6])[1]),
                'ipv6': int(re.findall(r'\d+', data[6])[2])
            },
            'TCP': {
                'total': int(re.findall(r'\d+', data[7])[0]),
                'ip': int(re.findall(r'\d+', data[7])[1]),
                'ipv6': int(re.findall(r'\d+', data[7])[2])
            },
            'INET': {
                'total': int(re.findall(r'\d+', data[8])[0]),
                'ip': int(re.findall(r'\d+', data[8])[1]),
                'ipv6': int(re.findall(r'\d+', data[8])[2])
            },
            'FRAG': {
                'total': int(re.findall(r'\d+', data[9])[0]),
                'ip': int(re.findall(r'\d+', data[9])[1]),
                'ipv6': int(re.findall(r'\d+', data[9])[2])
            }
        }
        return new_data


def send_mess_udp(mess, addr):
    # 通过 udp 发送数据
    # udp 是无状态的协议，没有发送失败这种情况，
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        if debug:
            test_stdout_fun(mess)
            test_stdout_fun(type(mess))
            test_stdout_fun(len(str(mess)))
        s.sendto(mess, addr)
        s.close()
    except socket.error:
        test_stdout_fun('udp socket error')
    except Exception, e:
        test_stdout_fun('udp send error')
        test_stdout_fun(str(e))


def send_mess_tcp(mess, addr):
    # 通过 tcp 发送数据
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((addr[0], addr[1]))
        if debug:
            test_stdout_fun(mess)
            test_stdout_fun(type(mess))
            test_stdout_fun(len(str(mess)))
        # s.sendto(mess,addr)
        s.send(mess)
        s.close()
        return True
    except socket.error, e:
        test_stdout_fun('tcp socket error')
        test_stdout_fun(e)
        return False
    except socket.timeout, e:
        test_stdout_fun('tcp socket timeout')
        test_stdout_fun(e)
        return False
    except Exception, e:
        test_stdout_fun('tcp send error')
        test_stdout_fun(str(e))
        return False


def test_stdout_fun(data):
    log_time = time.strftime('%Y-%m-%d %H:%M:%S'),
    f = open(logfile, 'a+')
    f.writelines(str(log_time) + ' - ' + str(data) + '\n')
    f.close()


def work_task(name):
    system_info = Local_info()
    network_info = Network_linux_info()

    if name == 'cpu_ram':
        mess_code = 1001
        body = {
            'cpu': system_info.get_cpu_stat_data(),
            'loadavg': system_info.get_loadavg(),
            'meminfo': system_info.get_meminfo()
        }

    if name == 'network':
        mess_code = 1002
        body = {
            'ss_status': network_info.get_network_ss_status(),
            'socket_status': network_info.get_socket_status(),
            'tcp_link_status': network_info.get_tcp_link_status(),
            'network_interface_info':
            network_info.get_network_interface_info()
        }

    if name == 'disk':
        mess_code = 1003
        body = {
            'disk_size': system_info.get_disk_data(),
            'disk_io': system_info.get_disk_io()
        }

    # if name == 'proc':
    #     body = {}
    #     mess_code = 1005

    mess = {
        'type': 'linux',
        'mess_type': 563982389,
        'hostname': platform.node(),
        'system_release': platform.dist()[0],
        'system_version': float(platform.dist()[1]),
        'ctime': time.strftime('%Y-%m-%d %H:%M:%S'),
        'mess_code': mess_code,
        'body': body
    }

    mess_body = json.dumps(mess)
    if not tcp_protocol:
        send_mess_udp(mess_body, server_addr)
    else:
        data = send_mess_tcp(mess_body, server_addr)
        if not data:
            test_stdout_fun('tcp link error: sleep 120')
            time.sleep(120)


def run_task():
    second_30 = minute_1 = minute_5 = minute_10 = minute_30 = minute_60 = 0
    # 初始化时间计数
    while True:
        atime = int(time.time())
        if atime >= second_30:
            # 每30s运行的任务
            second_30 = atime + 30
            work_task('cpu_ram')

        if atime >= minute_1:
            # 每 1 分钟运行的任务
            minute_1 = atime + 60
            work_task('network')

        if atime >= minute_10:
            # 每 10 分钟运行的任务
            minute_10 = atime + 600
            work_task('disk')

        time.sleep(1)


def work_start():
    # 两次 fork 脱离当前终端，离开当前路径
    if os.fork() > 0:
        os._exit(0)
    os.chdir('/')
    os.setsid()
    os.umask(0)
    pid = os.fork()
    if pid > 0:
        os._exit(0)
    else:
        sys.stdout.flush()
        sys.stderr.flush()
        si = file('/dev/null', 'r')
        so = file('/dev/null', 'a+')
        se = file('/dev/null', 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        pid = str(os.getpid())

        f = open(pidfile, 'w+')
        f.write("%s\n" % pid)
        f.close()

        run_task()


def work_stop():
    try:
        f = open(pidfile, 'r')
        pid = int(f.read().strip())
        f.close()
    except Exception, e:
        print 'pid file error'
        raise e
    os.kill(pid, SIGTERM)
    time.sleep(0.1)
    os.remove(pidfile)


def main():
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            work_start()
        elif 'stop' == sys.argv[1]:
            work_stop()
        elif 'restart' == sys.argv[1]:
            work_stop()
            work_start()
        else:
            print('unkonow command')
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage:%s start/stop/restart" % sys.argv[0])
        sys.exit(2)


if __name__ == '__main__':
    pidfile = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'bunnyc_agent.pid'))
    logfile = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'bunnyc_agent.log'))
    main()
    # work_task('cpu_ram')
    # work_task('network')
    # work_task('disk')
