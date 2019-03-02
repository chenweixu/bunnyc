# 2019-03-03 00:41:09
# Version: 0.01
# alarm

FROM chenwx716/python:3
MAINTAINER chenwx "chenwx716@163.com"

# install python pkg
RUN pip3 install PyYAML && pip3 install redis && pip3 install requests

# add bserver
ADD alarm /usr/local/alarm

# CMD
CMD python3 /usr/local/alarm/alarm.py
