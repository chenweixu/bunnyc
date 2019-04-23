#!/bin/bash

work_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/../ && pwd )"
cd $work_dir

version=0.2
conf_file=$work_dir/conf/devel.yaml

echo "=========================================="
echo "del run log: $work_dir"
echo "=========================================="
find $work_dir -name '*.log' -exec rm {} \;

cp $conf_file $work_dir/src/conf.yaml
echo 'copy devel.yaml to all service'

create_container() {
    local container=$1

    echo "=========================================="
    echo "build: $container"
    echo "=========================================="

    docker stop $container
    docker rm $container
    docker rmi chenwx/$container:$version

    docker build -t chenwx/$container:$version -f dockerfile/$container.dockerfile .
    docker run --name $container -h $container --net="host" -d chenwx/$container:$version
}


container_name=$1

if [ $container_name ]; then
    create_container $container_name
else
    echo 'no input arg, copy conf file'
fi


