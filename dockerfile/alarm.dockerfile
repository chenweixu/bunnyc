# 2019-03-03 00:41:09
# Version: 0.1
# alarm

FROM chenwx/bunnyc_platform:0.2
MAINTAINER chenwx "chenwx716@163.com"

# add alarm
ADD src/alarm.py /usr/local/
ADD src/conf.yaml /usr/local/

# CMD
CMD python3 /usr/local/alarm.py
