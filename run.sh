#!/usr/bin/env bash

sudo docker stop matilda
sudo docker rm matilda
sudo docker run -itd -p 9090:9090 --name matilda ccr.ccs.tencentyun.com/mioo/matilda