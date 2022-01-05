#!/bin/sh

set -e

docker build . -t grpcexample-v`date +"%Y%m%d%H%M%S"`
