#!/bin/bash

work_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp $work_dir/devel.yaml $work_dir/../alarm/conf.yaml
cp $work_dir/devel.yaml $work_dir/../bserver/conf.yaml
cp $work_dir/devel.yaml $work_dir/../gserver/conf.yaml
cp $work_dir/devel.yaml $work_dir/../mserver/conf.yaml
cp $work_dir/devel.yaml $work_dir/../moniter/conf.yaml
