import json
from lib.mylog import My_log
from lib.format_data import Format_data



class MserverTcpService(object):
    """docstring for MserverTcpService"""
    def __init__(self, data, wredis):
        super(MserverTcpService, self).__init__()
        self.data = data
        self.wredis = wredis
        self.work_log = My_log().get_log()
