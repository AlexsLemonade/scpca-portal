#!/bin/bash -e

python wait_for_postgres.py
export AWS_DEFAULT_REGION=us-east-1
coverage run ./manage.py test -v 2 --no-input "$@"
coverage report -m
