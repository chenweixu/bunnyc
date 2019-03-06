#!/bin/bash

work_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )"../ && pwd )"

#===================================================================

conf_file=$work_dir/conf/devel.yaml

cp $conf_file $work_dir/alarm/conf.yaml
cp $conf_file $work_dir/bserver/conf.yaml
cp $conf_file $work_dir/gserver/conf.yaml
cp $conf_file $work_dir/mserver/conf.yaml
cp $conf_file $work_dir/moniter/conf.yaml

#===================================================================

version=0.2

#------------------------------------------------
echo "=========================================="
echo "del run log: $work_dir"
echo "=========================================="
find $work_dir -name '*.log' -exec rm {} \;
#------------------------------------------------
# bserver
container=bserver

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#------------------------------------------------
# gserver
container=gserver

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#------------------------------------------------
# mserver
container=mserver

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#------------------------------------------------
# moniter
container=moniter

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#------------------------------------------------
# alarm
container=alarm

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#===================================================================
