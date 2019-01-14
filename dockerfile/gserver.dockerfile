# 2018-07-25 10:02:18
# Version: 0.01
# gserver

FROM python:3.7.0-alpine
MAINTAINER chenwx "chenwx716@163.com"

# set pip source
RUN mkdir -p /root/.config/pip
ADD pip.conf /root/.config/pip/pip.conf

# set timezone
COPY Shanghai /etc/localtime

# install python pkg
RUN pip install PyYAML && pip install redis && pip install python-memcached

# add bserver
ADD gserver /usr/local/gserver

# CMD
CMD /usr/local/bin/python /usr/local/gserver/run.py
