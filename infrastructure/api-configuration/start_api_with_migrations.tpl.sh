#!/bin/bash

chown -R ubuntu /home/ubuntu

STATIC_VOLUMES=/tmp/volumes_static
mkdir -p /tmp/volumes_static
chmod a+rwx /tmp/volumes_static

# Pull the API image.
api_docker_image=${dockerhub_repo}/scpca_portal_api:latest
docker pull $api_docker_image

# Migrate first.
# These database values are created after terraform
# is run, so we have to pass them in programatically
docker run \
       --env-file environment \
       -v "$STATIC_VOLUMES":/tmp/www/static \
       --log-driver=awslogs \
       --log-opt awslogs-region=${region} \
       --log-opt awslogs-group=${log_group} \
       --log-opt awslogs-stream=${log_stream} \
       -p 8081:8081 \
       --name=scpca_portal_migrations \
       $api_docker_image python3 manage.py migrate

# Start the API image.
docker run \
       --env-file environment \
       -v "$STATIC_VOLUMES":/tmp/www/static \
       --log-driver=awslogs \
       --log-opt awslogs-region=${region} \
       --log-opt awslogs-group=${log_group} \
       --log-opt awslogs-stream=${log_stream} \
       -p 8081:8081 \
       --name=scpca_portal_api \
       -d $api_docker_image

docker exec scpca_portal_api python3 manage.py collectstatic --noinput
