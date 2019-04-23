# 2018-07-25 10:02:18
# Version: 0.1
# mserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add mserver
ADD src/mserver.py /usr/local/
ADD src/conf.yaml /usr/local/
ADD src/lib /usr/local/lib

# CMD
CMD python3 /usr/local/mserver/run.py
