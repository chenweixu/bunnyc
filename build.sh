#!/bin/bash
# 0.1         2018-12-25 15:28:12

version=0.1

work_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
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
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file

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
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file
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
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file

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
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file

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
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file
#===================================================================

docker run --name bserver -h bserver --net="host" -d chenwx/bserver:$version
docker run --name mserver -h mserver --net="host" -d chenwx/mserver:$version
docker run --name gserver -h gserver --net="host" -d chenwx/gserver:$version
docker run --name moniter -h moniter --net="host" -d chenwx/moniter:$version
docker run --name alarm -h alarm --net="host" -d chenwx/alarm:$version
