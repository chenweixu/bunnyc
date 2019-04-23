
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from lib.dbmodel import t_host_cpu, t_host_ram, t_memcached


class BunnycDB(object):
    """docstring for BunnycDB"""
    def __init__(self, dblink):
        super(BunnycDB, self).__init__()

        engine = create_engine(dblink)
        # engine = create_engine('mysql+pymysql://bunnyc:passw8rd@localhost:3306/bunnyc')
        DBSession = sessionmaker(bind=engine)

        # 创建session对象:
        self.session = DBSession()

    def __del__(self):
        try:
            if hasattr(self, "session"):
                print('clone session')
                self.session.close()
        except Exception:
            pass

    def inster_t_host_ram(self,data):
        new_data = t_host_ram(
            ctime = data.get('ctime'),
            ip = data.get('ip'),
            mem = data.get('mem_used_rate'),
            swap = data.get('swap_used_rate')
            )
        # 添加到session:
        self.session.add(new_data)

        # 提交即保存到数据库:
        self.session.commit()

    def inster_t_host_cpu(self,data):

        new_data = t_host_cpu(
            ctime = data.get('ctime'),
            ip = data.get('ip'),
            cpu = data.get('cpu_rate'),
            cpu_user_rate = data.get('cpu_user_rate'),
            cpu_nice_rate = data.get('cpu_nice_rate'),
            cpu_system_rate = data.get('cpu_system_rate'),
            cpu_idle_rate = data.get('cpu_idle_rate'),
            cpu_iowait_rate = data.get('cpu_iowait_rate'),
            cpu_irq_rate = data.get('cpu_irq_rate'),
            cpu_softirq_rate = data.get('cpu_softirq_rate'),
            ld_1 = data.get('ld_1'),
            ld_2 = data.get('ld_5'),
            ld_3 = data.get('ld_15'),
            proc_run = data.get('proc_run'),
            proc_sub = data.get('proc_sum')
            )
        # 添加到session:
        self.session.add(new_data)

        # 提交即保存到数据库:
        self.session.commit()


    def inster_t_memcached(self,data):
        new_data = t_memcached(
            mcid = int(data.get('strid').strip('mc')),
            mcport = data.get('port'),
            ctime = data.get('ctime'),
            ip = data.get('ip'),
            memsum = data.get('memsum'),
            memused = data.get('memused'),
            cmd_get = data.get('cmd_get'),
            cmd_set = data.get('cmd_set'),
            get_hits = data.get('get_hits'),
            curr_connections = data.get('curr_connections'),
            total_connections = data.get('total_connections')
            )
        # 添加到session:
        self.session.add(new_data)

        # 提交即保存到数据库:
        self.session.commit()


    def select_t_host_ram(self):
        # 创建Query查询，filter是where条件，
        # 最后调用one()返回唯一行，如果调用all()则返回所有行:
        f = self.session.query(t_host_ram).filter(t_host_ram.id=='2').one()

        print('type:', type(f))
        print('name:', f.mem)
        print('name:', type(f.mem))

