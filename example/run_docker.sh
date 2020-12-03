#!/bin/bash
NAME=px_python3_wsgi

docker rm -v -f $NAME || true
docker build  -t $NAME -f Dockerfile .
docker run \
    -v $(pwd)/:/tmp/px \
    -p 8080:8080 \
    -it --name $NAME $NAME
