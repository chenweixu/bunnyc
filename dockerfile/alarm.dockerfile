# 2019-03-03 00:41:09
# Version: 0.1
# alarm

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD alarm /usr/local/alarm

# CMD
CMD python3 /usr/local/alarm/alarm.py
