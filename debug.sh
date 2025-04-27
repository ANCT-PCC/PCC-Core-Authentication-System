docker compose stop && docker rm pcc-cas &&  docker rmi pcc-core-authentication-system-pcc-cas && docker compose up -d
docker system prune -f
date