#!/usr/bin/env bash

sudo docker build --rm -t matilda .
sudo docker tag matilda:latest ccr.ccs.tencentyun.com/mioo/matilda:latest
sudo docker push ccr.ccs.tencentyun.com/mioo/matilda:latest