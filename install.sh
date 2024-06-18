#!/bin/bash

docker volume create pcc-cas-db
docker run --name pcc-cas-db --restart=always -d -v pcc-cas-db:/var/lib/mysql -e MYSQL_ROOT_PASSWORD -p 3306:3306 mysql:latest

###############################################################################
# Create setting_files/admin_info.json before run ./install.sh in root user.  #
###############################################################################

docker image build -t pcc-cas:latest . 
docker volume create pcc-cas
docker run --name pcc-cas --restart=always -p 8080:8080 -d -v pcc-cas:/PCC-CAS -t pcc-cas:latest