#!/bin/bash

# Zip letsencrypt dir
cd /home/ubuntu
zip -r letsencrypt.zip /etc/letsencrypt/ /etc/nginx/nginx.conf

# Sync with S3
aws s3 cp letsencrypt.zip "s3://${scpca_portal_cert_bucket}/"
rm letsencrypt.zip
