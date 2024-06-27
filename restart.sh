#!/bin/bash

docker-compose down
docker rmi pcc-core-authentication-system-pcc-cas
docker-compose up -d