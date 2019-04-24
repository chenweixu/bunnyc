# 2019-03-03 00:41:17
# Version: 0.1
# monitor

FROM chenwx/bunnyc_platform:0.2
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD src/monitor.py /usr/local/
ADD src/conf.yaml /usr/local/

# CMD
CMD python3 /usr/local/monitor.py
