# 2018-07-25 10:02:18
# Version: 0.01
# mserver

FROM python:3.7.0-alpine
MAINTAINER chenwx "chenwx716@163.com"

# set pip source
RUN mkdir -p /root/.config/pip
ADD pip.conf /root/.config/pip/pip.conf

# install python pkg
RUN pip install PyYAML && pip install redis && pip install PyMySQL

# add mserver
ADD mserver /usr/local/mserver

# CMD
CMD /usr/local/bin/python /usr/local/mserver/run.py
