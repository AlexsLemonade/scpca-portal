#!/bin/bash

chown -R ubuntu:ubuntu /home/ubuntu

STATIC_VOLUMES=/var/www/volumes_static
mkdir -p "$STATIC_VOLUMES"
chown -R ubuntu:ubuntu "$STATIC_VOLUMES"

# Pull the API image.
api_docker_image=${dockerhub_repo}/scpca_portal_api:latest
docker pull $api_docker_image

# Migrate first.
docker run \
    --env-file environment \
    --log-driver=awslogs \
    --log-opt awslogs-region=${region} \
    --log-opt awslogs-group=${log_group} \
    --log-opt awslogs-stream=${log_stream} \
    --name=scpca_portal_migrations \
    --platform linux/amd64 \
    $api_docker_image python3 manage.py migrate

# Start the API image.
docker run \
    --env-file environment \
    --log-driver=awslogs \
    --log-opt awslogs-region=${region} \
    --log-opt awslogs-group=${log_group} \
    --log-opt awslogs-stream=${log_stream} \
    --name=scpca_portal_api \
    --platform linux/amd64 \
    --restart unless-stopped \
    -d \
    -p 8081:8081 \
    -v "$STATIC_VOLUMES":/tmp/www/static \
    $api_docker_image

# Collect static.
docker exec scpca_portal_api python3 manage.py collectstatic --noinput

# Configure AWS CLI.
docker exec scpca_portal_api python3 manage.py configure_aws_cli
