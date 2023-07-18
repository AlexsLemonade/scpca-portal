#!/bin/bash

API_DOCKER_IMAGE="${dockerhub_repo}/scpca_portal_api:latest"

# Pull the API image.
docker pull "$API_DOCKER_IMAGE"

# Start the API image.
docker run \
    --env-file environment \
    --name scpca_portal_loader \
    --rm "$API_DOCKER_IMAGE" \
    python3 manage.py "$@"
