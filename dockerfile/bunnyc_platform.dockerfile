# 2019-03-06 08:24:39
# Version: 0.2

# docker build -t chenwx/bunnyc_platform:0.2 -f dockerfile/bunnyc_platform.dockerfile .

FROM chenwx/python:3
MAINTAINER chenwx "chenwx716@163.com"

# install systemd pkg
RUN apk add --no-cache py3-cffi py3-cryptography

# install python pkg
ADD requirements.txt /usr/local/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir -r /usr/local/requirements.txt \
    && rm /usr/local/requirements.txt
