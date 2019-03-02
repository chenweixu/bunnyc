# 2018-07-25 10:02:18
# Version: 0.01
# gserver

FROM chenwx716/python:3
MAINTAINER chenwx "chenwx716@163.com"

# install python pkg
RUN pip3 install PyYAML && pip3 install redis && pip3 install pymemcache

# add bserver
ADD gserver /usr/local/gserver

# CMD
CMD python3 /usr/local/gserver/run.py
