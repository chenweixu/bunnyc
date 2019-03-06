# 2018-07-25 10:02:18
# Version: 0.1
# mserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add mserver
ADD mserver /usr/local/mserver

# CMD
CMD python3 /usr/local/mserver/run.py
