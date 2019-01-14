import re
from ipaddress import ip_address
from lib.conf import conf_data

host_to_as = conf_data('host_to_as')


class resolve_host_data(object):
    """docstring for resolve_host_data
    主要是为了处理linux报文日志中的一些数据格式
    mess 的 type 需要为 101
    """

    def __init__(self, data):
        super(resolve_host_data, self).__init__()
        self.data = data

    def get_cpu_run_data(self):
        # CPU 使用率信息
        value = self.data.get('cpu')

        def Less(x, y):
            return x - y

        total = sum(value[1]) - sum(value[0])
        total_used = map(Less, value[1], value[0])

        def f_rate(x):
            return round(float(x) / total * 100, 2)

        cpu_stat = list(map(f_rate, total_used))
        cpu_rate = round(100 - cpu_stat[3], 2)

        cpuinfo = {
            'cpu_rate': cpu_rate,
            'cpu_user_rate': cpu_stat[0],
            'cpu_nice_rate': cpu_stat[1],
            'cpu_system_rate': cpu_stat[2],
            'cpu_idle_rate': cpu_stat[3],
            'cpu_iowait_rate': cpu_stat[4],
            'cpu_irq_rate': cpu_stat[5],
            'cpu_softirq_rate': cpu_stat[6]
        }
        return cpuinfo

    def get_mem_rate(self):
        # 内存使用率
        value = self.data.get('meminfo')
        if value.get('SReclaimable'):
            mem_used = int(value.get('MemTotal')) - int(
                value.get('MemFree')) - int(value.get('Buffers')) - int(
                    value.get('Cached')) - int(value.get('SReclaimable'))
        else:
            mem_used = int(value.get('MemTotal')) - int(
                value.get('MemFree')) - int(value.get('Buffers')) - int(
                    value.get('Cached'))

        mem_rate = round((float(mem_used) / int(value.get('MemTotal'))) * 100,
                         2)
        return mem_rate

    def get_swap_rate(self):
        # SWAP使用率
        value = self.data.get('meminfo')
        swap_user = (float(value.get('SwapTotal')) - int(
            value.get('SwapFree'))) / int(value.get('SwapTotal')) * 100
        swap_user_r = round(swap_user)
        return swap_user_r

    def get_loadavg(self):
        # CPU负载信息和CPU任务数信息
        value = self.data.get('loadavg')
        ld = {
            'ld_1': float(value[0]),
            'ld_5': float(value[1]),
            'ld_15': float(value[2]),
            'proc_run': int(value[3].split('/')[0]),
            'proc_sum': int(value[3].split('/')[1])
        }
        return ld

    def get_netinterface_info(self):
        # 网卡流量和包异常状态
        value = self.data.get('network_interface_info')
        new_data = {}
        for i in value:
            new_data[i[0]] = {
                'rbytes': i[1],
                'rpackets': i[2],
                'rerrs': i[3],
                'rdrop': i[4],
                'rfifo': i[5],
                'rframe': i[6],
                'rcompressed': i[7],
                'rmulticast': i[8],
                'tbytes': i[9],
                'tpackets': i[10],
                'terrs': i[11],
                'tdrop': i[12],
                'tfifo': i[13],
                'tframe': i[14],
                'tcompressed': i[15],
                'tmulticast': i[16]
            }
        return new_data

    def get_disk_space_info(self):
        value = self.data.get('disk_size')
        disk_info = {}
        for i in value:
            disk_info[i[-1]] = {
                'dev': i[0],
                'sum': i[1],
                'used': i[2],
                'free': i[3],
                'rate': int(i[4].rstrip('%')),
                'name': i[5]
            }
        return disk_info

    def get_iostatus(self):
        value = self.data.get('disk_io')
        iostatus = {}
        for i in value:
            iostatus[i[0]] = {
                'tps': float(i[1]),
                'Blk_read': float(i[2]),
                'Blk_wrtn': float(i[3]),
                'Blk_read': int(i[4]),
                'Blk_wrtn': int(i[5])
            }
        return iostatus

    def get_socket_status(self):
        value = self.data.get('socket_status')
        tcp_info = re.findall(r'\d+', value[1])
        udp_info = re.findall(r'\d+', value[2])

        if 'UDPLITE' not in value[3]:
            value.insert(2, 'UDPLITE: inuse 0')

        new_data = {
            'used': int(re.findall(r'\d+', value[0])[0]),
            'tcp': {
                'inuse': int(tcp_info[0]),
                'orphan': int(tcp_info[1]),
                'tw': int(tcp_info[2]),
                'alloc': int(tcp_info[3]),
                'mem': int(tcp_info[4])
            },
            'udp': {
                'inuse': int(udp_info[0]),
                'mem': int(udp_info[1])
            },
            'udplite': {
                'inuse': int(re.findall(r'\d+', value[3])[0])
            },
            'raw': {
                'inuse': int(re.findall(r'\d+', value[4])[0])
            },
            'frag': {
                'inuse': int(re.findall(r'\d+', value[5])[0]),
                'memory': int(re.findall(r'\d+', value[5])[1])
            }
        }
        return new_data


class Modify_data(object):
    """docstring for Modify_data"""

    def __init__(self):
        super(Modify_data, self).__init__()

    def modify_linux_data(self, data):
        # 将原始的数据格式转换为规范的格式

        body_txt = data.get('body')
        resolve_data = resolve_host_data(body_txt)
        mess_code = data.get('mess_code')

        try:

            if mess_code == 1001:
                new_data = {
                    'strid': host_to_as.get(data.get('ip')),
                    'ctime': data.get('ctime'),
                    'gtime': data.get('gtime'),
                    'type': data.get('type'),
                    'ip': data.get('ip'),
                    'intip': int(ip_address(data.get('ip'))),
                    'mess_code': mess_code,
                    'cpu': resolve_data.get_cpu_run_data(),
                    'loadavg': resolve_data.get_loadavg(),
                    'mem_used_rate': resolve_data.get_mem_rate(),
                    'swap_used_rate': resolve_data.get_swap_rate(),
                    'meminfo': body_txt.get('meminfo')
                }
                return new_data

            elif mess_code == 1002:
                new_data = {
                    'strid': host_to_as.get(data.get('ip')),
                    'ctime': data.get('ctime'),
                    'gtime': data.get('gtime'),
                    'type': data.get('type'),
                    'ip': data.get('ip'),
                    'intip': int(ip_address(data.get('ip'))),
                    'mess_code': mess_code,
                    'ss_status': body_txt.get('ss_status'),
                    'socket_status': resolve_data.get_socket_status(),
                    'tcp_link_status': body_txt.get('tcp_link_status'),
                    'network_interface_info':
                    resolve_data.get_netinterface_info()
                }
                return new_data

            elif mess_code == 1003:
                new_data = {
                    'strid': host_to_as.get(data.get('ip')),
                    'ctime': data.get('ctime'),
                    'gtime': data.get('gtime'),
                    'type': data.get('type'),
                    'ip': data.get('ip'),
                    'intip': int(ip_address(data.get('ip'))),
                    'mess_code': mess_code,
                    'disk_size': resolve_data.get_disk_space_info(),
                    'disk_io': resolve_data.get_iostatus()
                }
                return new_data

            else:
                return False

        except Exception as e:
            raise

            # new_data = {
            #     'strid': host_to_as.get(data.get('ip')),
            #     'ctime': data.get('ctime'),
            #     'type': data.get('type'),
            #     'ip': data.get('ip'),
            #     'intip': int(ip_address(data.get('ip'))),
            #     'cpu': info.get_cpu_run_data(),
            #     'loadavg': info.get_loadavg(),
            #     'mem_used_rate': info.get_mem_rate(),
            #     'swap_used_rate': info.get_swap_rate(),
            #     'meminfo': data.get('meminfo'),
            #     'disk_size': info.get_disk_space_info(),
            #     'disk_io': info.get_iostatus(),
            #     'ss_status': data.get('ss_status'),
            #     'socket_status': info.get_socket_status(),
            #     'tcp_link_status': data.get('tcp_link_status'),
            #     'network_interface_info': info.get_netinterface_info()
            # }
        #     return new_data
        # except Exception as e:
        #     raise e
