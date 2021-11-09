#!/bin/bash -e

python wait_for_postgres.py
mkdir /home/user/code/test_data/
export AWS_DEFAULT_REGION=us-east-1
aws s3 ls s3://scpca-portal-public-test-inputs --no-sign-request
aws s3 sync --delete s3://scpca-portal-public-test-inputs /home/user/code/test_data/ --no-sign-request
coverage run ./manage.py test -v 2 --no-input "$@"
coverage report -m
