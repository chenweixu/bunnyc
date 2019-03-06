#!/bin/bash
# 0.1         2018-12-25 15:28:12

version=0.1

work_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$work_dir/conf/devel.sh
# $work_dir/conf/produce.sh

#------------------------------------------------
echo "=========================================="
echo "del run log: $work_dir"
echo "=========================================="
find $work_dir -name '*.log' -exec rm {} \;
#------------------------------------------------
# bserver
container=bserver
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

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
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

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
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

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
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

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
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

echo "=========================================="
echo "build: $container"
echo "=========================================="

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .

#===================================================================
