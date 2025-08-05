#!/bin/bash

set -e

python3 wait_for_postgres.py
export AWS_DEFAULT_REGION=us-east-1
./manage.py configure_aws_cli
coverage run ./manage.py test -v 2 --no-input "$@"
coverage report -m
