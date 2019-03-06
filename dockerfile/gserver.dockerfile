# 2018-07-25 10:02:18
# Version: 0.1
# gserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD gserver /usr/local/gserver

# CMD
CMD python3 /usr/local/gserver/run.py
