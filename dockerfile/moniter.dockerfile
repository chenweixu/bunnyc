# 2019-03-03 00:41:17
# Version: 0.1
# moniter

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD moniter /usr/local/moniter

# CMD
CMD python3 /usr/local/moniter/moniter.py
