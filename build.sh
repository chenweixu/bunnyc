#!/bin/bash
# 0.1         2018-12-25 15:28:12

#------------------------------------------------
# bserver
version=0.1
container=bserver
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/bserver.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file

#------------------------------------------------
# gserver
version=0.1
container=gserver
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/gserver.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file
#------------------------------------------------
# mserver
version=0.1
container=mserver
img_dir=/data/share/docker_images
img_file=$img_dir/chenwx_${container}_${version}.tar

docker stop $container
docker rm $container
docker rmi chenwx/$container:$version
rm $img_dir/chenwx_$container_$version.tar

docker build -t chenwx/$container:$version -f dockerfile/mserver.dockerfile .
sleep 2
docker save chenwx/$container:$version > $img_file
#===================================================================

docker run --name bserver -h bserver --net="host" -d chenwx/bserver:$version
docker run --name mserver -h mserver --net="host" -d chenwx/mserver:$version
docker run --name gserver -h gserver --net="host" -d chenwx/gserver:$version
