import time
import threading
import socket
import json
from lib.conf import conf_data
from lib.mylog import My_log


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

        work_log = My_log().get_log()
        listen_port = conf_data('bserver', 'port')

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
            data = connection.recv(2048)
            connection.close()
            work_log.debug('input tcp data from ip: ' + client_ip)
            try:
                info = json.loads(data.decode('utf-8'))
                if info.get('mess_type') == 563982389:
                    info['ip'] = client_ip
                    info['gtime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.queue.put(info)
                    work_log.debug('send tcp data to queue success: ' +
                                   client_ip)
                else:
                    work_log.error(client_ip + ',' + 'mess_type error')
            except ValueError as e:
                work_log.error(client_ip + ': ' + str(e))
            except Exception as e:
                work_log.error(client_ip + ': ' + str(e))
        server.close()
