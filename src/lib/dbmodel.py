import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, SmallInteger, String, Float, DateTime

# 创建对象的基类:
Base = declarative_base()

class t_host_cpu(Base):
    """定义数据模型"""
    __tablename__ = 't_host_cpu'

    id = Column(Integer, primary_key=True,autoincrement=True)
    ctime = Column(DateTime,nullable=False, comment='采集时间',index=True)
    itime = Column(DateTime,nullable=False, default=datetime.datetime.now, comment='入库时间')
    ip = Column(String(20),nullable=False,comment='服务器IP')
    cpu = Column(Float(5,2),nullable=False,comment='使用率')
    cpu_user_rate = Column(Float(5,2),nullable=False,comment='用户态')
    cpu_nice_rate = Column(Float(5,2),nullable=False,comment='权限调整')
    cpu_system_rate = Column(Float(5,2),nullable=False,comment='内核态')
    cpu_idle_rate = Column(Float(5,2),nullable=False,comment='空闲')
    cpu_iowait_rate = Column(Float(5,2),nullable=False,comment='IO阻塞')
    cpu_irq_rate = Column(Float(5,2),nullable=False,comment='硬中断')
    cpu_softirq_rate = Column(Float(5,2),nullable=False,comment='软中断')
    ld_1 = Column(Float(5,2),nullable=False,comment='1分钟负载')
    ld_2 = Column(Float(5,2),nullable=False,comment='5分钟负载')
    ld_3 = Column(Float(5,2),nullable=False,comment='15分钟负载')
    proc_run = Column(SmallInteger(),nullable=False,comment='当前运行pid')
    proc_sub = Column(SmallInteger(),nullable=False,comment='合计PID数')


class t_host_ram(Base):
    """定义数据模型"""
    __tablename__ = 't_host_ram'

    id = Column(Integer, primary_key=True,autoincrement=True)
    ctime = Column(DateTime,nullable=False, comment='采集时间',index=True)
    itime = Column(DateTime, default=datetime.datetime.now, comment='入库时间')
    ip = Column(String(20),nullable=False,comment='服务器IP')
    mem = Column(SmallInteger(),nullable=False,comment='内存使用率')
    swap = Column(SmallInteger(),nullable=False,comment='swap使用率')

class t_memcached(Base):
    """定义数据模型"""
    __tablename__ = 't_memcached'

    id = Column(Integer, primary_key=True,autoincrement=True)
    mcid = Column(SmallInteger(),nullable=False,comment='MCID')
    mcport = Column(SmallInteger(),nullable=False,comment='MCPORT')
    ctime = Column(DateTime,nullable=False, comment='采集时间',index=True)
    itime = Column(DateTime, default=datetime.datetime.now, comment='入库时间')
    ip = Column(String(20),nullable=False,comment='服务器IP')
    memsum = Column(Integer(),nullable=False,comment='内存总量')
    memused = Column(Integer(),nullable=False,comment='使用内存')
    cmd_get = Column(Integer(),nullable=False,comment='GET数')
    cmd_set = Column(Integer(),nullable=False,comment='SET数')
    get_hits = Column(Integer(),nullable=False,comment='GET命中数')
    curr_connections = Column(SmallInteger(),nullable=False,comment='当前连接数')
    total_connections = Column(Integer(),nullable=False,comment='总连接数')

