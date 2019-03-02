from pymemcache.client import Client
import json


def serialize_json(key, value):
    """
    构造函数；用于将非 str 类型的数据转换成 str 类型存入memc
    """
    # if type(value) == str:
    #     return value, 32
    if type(value) == dict:
        return json.dumps(value), 37
    else:
        return value, 32


def deserialize_json(key, value, flags):
    """
    解析函数
    用于将 str 类型的数据解析成应用需要的格式
    此处的 flags 实质上是从 memc 中取到的
    """
    if flags == 0:
        return value
    elif flags == 32:
        return value
    elif flags == 37:
        return json.loads(value)
    else:
        return value


class Memcached(object):
    """docstring for Memcached
    基础的 memcache 使用抽象类
    """

    def __init__(self, ip, port):
        super(Memcached, self).__init__()
        # link = [str(ip) + ":" + str(port)]
        self.mc = Client(
            (ip, int(port)),
            serializer=serialize_json,
            deserializer=deserialize_json,
            connect_timeout=2,
        )

    def stats(self):
        return self.mc.stats()

    def show_stats(self, key):
        return self.stats().get(key.encode())


    def get(self, key):
        data = self.mc.get(key.encode())
        if data:
            return data.decode()
        return data
        # else:
        # return 'None Value'

    def delete(self, key):
        return self.mc.delete(key.encode())

    def set(self, key, value, expire=600):
        return self.mc.set(key, value, expire)
        # data = bytes(value,encoding="utf-8")
        # return self.mc.set(key,data,expire)

    def get_connections_sum(self):
        return int(self.stats().get("curr_connections".encode()))

    def get_mem_rate(self):
        data = self.stats()
        memsum = int(data.get("limit_maxbytes".encode()))
        memused = int(data.get("bytes".encode()))
        return round(memused / memsum * 100, 2)

    def flush_all(self):
        return self.mc.flush_all()
