#!/bin/bash

# Zip letsencrypt dir
cd /home/ubuntu
zip -r letsencryptdir.zip /etc/letsencrypt/ /etc/nginx/nginx.conf

# Sync with S3
aws s3 cp letsencryptdir.zip "s3://${scpca_portal_cert_bucket}/"
rm letsencryptdir.zip
