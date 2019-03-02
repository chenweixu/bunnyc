# 2018-07-25 10:02:18
# Version: 0.01
# bserver

FROM chenwx716/python:3
MAINTAINER chenwx "chenwx716@163.com"

# install python pkg
RUN pip3 install PyYAML && pip3 install redis

# add bserver
ADD bserver /usr/local/bserver

# CMD
CMD python3 /usr/local/bserver/run.py

EXPOSE 8716
