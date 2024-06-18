#!/bin/bash

docker stop pcc-cas
docker rm pcc-cas
docker rmi pcc-cas
docker volume remove pcc-cas