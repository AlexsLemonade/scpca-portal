#!/bin/bash

# Pull the API image.
api_docker_image=${dockerhub_repo}/scpca_portal_api:latest
docker pull $api_docker_image


# Start the API image.
docker run \
       --env-file environment \
       --name=scpca_portal_loader \
       -d $api_docker_image python3 manage.py load_data "$@"

docker exec scpca_portal_api pwd
