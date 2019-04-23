#!/bin/bash

version=0.2

img_dir=/data/share/docker_images

# bproxy
container=bproxy
img_file=$img_dir/chenwx_${container}_${version}.tar

rm $img_file
docker save chenwx/$container:$version > $img_file

# gserver
container=gserver
img_file=$img_dir/chenwx_${container}_${version}.tar

rm $img_file
docker save chenwx/$container:$version > $img_file

# mserver
container=mserver
img_file=$img_dir/chenwx_${container}_${version}.tar

rm $img_file
docker save chenwx/$container:$version > $img_file

# monitor
container=monitor
img_file=$img_dir/chenwx_${container}_${version}.tar

rm $img_file
docker save chenwx/$container:$version > $img_file

# alarm
container=alarm
img_file=$img_dir/chenwx_${container}_${version}.tar

rm $img_file
docker save chenwx/$container:$version > $img_file

