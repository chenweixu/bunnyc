import time
import threading
import socket
import json
from lib.conf import conf_data
from lib.mylog import My_log


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
        work_log = My_log().get_log()
        listen_port = conf_data('bserver', 'port')

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
                    pass
                    # work_log.error(addr[0]+','+str(e))

                if info.get('mess_type') == 563982389:
                    info['ip'] = addr[0]
                    info['gtime'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.queue.put(info)
                    work_log.debug('send udp date to queue success: ' +
                                   addr[0])
                    work_log.debug('Net_udp_server mess_code: ' +
                                   str(info.get('mess_code')))
                else:
                    work_log.error(addr[0] + ',' + 'mess_type error')
            except ValueError as e:
                work_log.error(addr[0] + ': ' + str(e))
            except Exception as e:
                work_log.error(addr[0] + ': ' + str(e))
        s.close()
