# 2018-07-25 10:02:18
# Version: 0.1
# bserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD bserver /usr/local/bserver

# CMD
CMD python3 /usr/local/bserver/run.py

EXPOSE 8716
