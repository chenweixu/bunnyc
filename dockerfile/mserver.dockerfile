# 2018-07-25 10:02:18
# Version: 0.01
# mserver

FROM chenwx716/python:3
MAINTAINER chenwx "chenwx716@163.com"

RUN apk add py3-cffi py3-cryptography
# PyMySQL 在 alpine 平台上的依赖项

# install python pkg
RUN pip3 install PyYAML && pip3 install redis && pip3 install PyMySQL

# add mserver
ADD mserver /usr/local/mserver

# CMD
CMD python3 /usr/local/mserver/run.py
