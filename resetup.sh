#!/bin/bash

docker-compose stop
docker rm pcc-cas-db
docker rmi mysql
rm -r mysql/

docker-compose up -d