# 2019-03-27 16:45:50
# Version: 0.1
# bserver

FROM chenwx/bunnyc_platform:0.1
MAINTAINER chenwx "chenwx716@163.com"

# add bserver
ADD bserver.py /usr/local/

# CMD
CMD python3 /usr/local/bserver.py

EXPOSE 8716
