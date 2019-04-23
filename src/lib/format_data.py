from ipaddress import ip_address
from lib.format_data_host import resolve_host_data

class Format_data(object):
    """docstring for Format_data"""
    def __init__(self):
        super(Format_data, self).__init__()

    def format_host_data(self, data, host_to_as):
        # 将原始的数据格式转换为规范的格式

        body_txt = data.get('body')
        resolve_data = resolve_host_data(body_txt)
        mess_code = data.get('mess_code')

        try:
            mess = {
                'strid': host_to_as.get(data.get('ip')),
                'ctime': data.get('ctime'),
                'gtime': data.get('gtime'),
                'type': data.get('type'),
                'ip': data.get('ip'),
                'intip': int(ip_address(data.get('ip'))),
                'mess_code': mess_code,
            }

            if mess_code == 1001:
                mess.update(resolve_data.get_cpu_run_data())
                mess.update(resolve_data.get_loadavg())
                return mess

            elif mess_code == 1002:
                mess.update(body_txt.get('meminfo'))
                mess['mem_used_rate'] = resolve_data.get_mem_rate()
                mess['swap_used_rate'] = resolve_data.get_swap_rate()
                return mess

            elif mess_code == 1003:
                mess['ss_status'] = str(body_txt.get('ss_status'))
                mess['socket_status'] = str(resolve_data.get_socket_status())
                mess['tcp_link_status'] = str(body_txt.get('tcp_link_status'))
                mess['network_interface_info'] = str(resolve_data.get_netinterface_info())
                return mess

            elif mess_code == 1004:
                partition, disk_size = resolve_data.get_disk_space_info()
                mess['partition'] = str(partition)
                mess.update(disk_size)

                iodevice, iostatus = resolve_data.get_iostatus()
                mess['iodevice'] = str(iodevice)
                mess.update(iostatus)
                return mess
            else:
                return False

        except Exception as e:
            raise

    def format_webService_data(self,data):
        body = data.get('body')
        new_data = []
        status_info = ""

        for i in body:
            status = i.get('status')
            if status == 200:
                status = 0
                status_info = "ok"
            elif status == 9:
                status_info = "timeout"
            else:
                status_info = "error"

            key = "monitor:"+ str(data.get("mess_code")) + ":" + i.get('name')
            value = {
                "type": data.get("type"),
                "name": i.get('name'),
                "url": i.get('url'),
                "status": status,
                "status_info": status_info,
                "ctime": data.get("ctime")
            }
            new_data.append([key, value])
        return new_data
