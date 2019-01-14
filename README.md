# bunnyC
python练习项目，主要用于服务器的监控

## 概述
该脚本为我在某项目做运维期间所使用的数据采集程序，
目的是方便做性能数据统计和自动生成运行质量报告,以及python学习练手；

## 组件说明
    agent: 服务器端的数据采集脚本
    bserver: 通过tcp和udp端口接收agent传来的数据，存入redis队列
    gserver: 主动数据采集脚本，采集数据存入 redis队列
    mserver: 将redis队列中的数据提出转换处理，存入mysql

# 待办
## agent
1. 添加进程监控
2. 从注册中心获取需要监控的指标

## mserver
1. 数据库支持 mongodb 和 elasticsearch

## gserver
1. 增加 http 服务指标获取

## 通知组件
1. 获取异常指标，发送告警数据

## 报表组件
1. 每日生成一份报表xlsx，通过email发送
2. 邮件html化，内嵌昨日的运行图表和数据表单

## 其它
1. 引入配置中心
