# 2019-03-03 00:41:17
# Version: 0.1
# monitor

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD monitor /usr/local/monitor

# CMD
CMD python3 /usr/local/monitor/monitor.py
