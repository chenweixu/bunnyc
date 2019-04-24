# 2019-03-27 16:45:50
# Version: 0.1
# bproxy

FROM chenwx/bunnyc_platform:0.2
MAINTAINER chenwx "chenwx716@163.com"

# add bproxy
ADD src/bproxy.py /usr/local/
ADD src/conf.yaml /usr/local/

# CMD
CMD python3 /usr/local/bproxy.py

EXPOSE 8716
