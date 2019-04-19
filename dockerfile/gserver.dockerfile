# 2019-03-27 16:45:56
# Version: 0.1
# gserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD gserver.py /usr/local/

# CMD
CMD python3 /usr/local/gserver.py
