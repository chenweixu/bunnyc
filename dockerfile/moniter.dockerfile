# 2019-03-03 00:41:17
# Version: 0.01
# moniter

FROM chenwx716/python:3
MAINTAINER chenwx "chenwx716@163.com"

# install python pkg
RUN pip3 install PyYAML && pip3 install redis && pip3 install requests

# add bserver
ADD moniter /usr/local/moniter

# CMD
CMD python3 /usr/local/moniter/moniter.py
