#!/bin/bash

API_DOCKER_IMAGE="${dockerhub_repo}/scpca_portal_api:latest"

# Prepare the data volume.
DATA_VOLUME_PATH="/home/ubuntu/data"
if [ ! -d "$DATA_VOLUME_PATH" ]; then
    mkdir "$DATA_VOLUME_PATH"
fi
chmod -R a+rwX "$DATA_VOLUME_PATH"

# Pull the API image.
docker pull "$API_DOCKER_IMAGE"

# Start the API image.
docker run \
    --env-file environment \
    --name scpca_portal_loader \
    --rm \
    --volume "$DATA_VOLUME_PATH:/home/user/data" \
    "$API_DOCKER_IMAGE" \
    python3 manage.py "$@"
