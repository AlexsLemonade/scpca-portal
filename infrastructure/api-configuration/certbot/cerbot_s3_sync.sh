#!/bin/bash

# Add the nginx.conf file that certbot setup to the zip dir.
cp /etc/nginx/nginx.conf /etc/letsencrypt/

# Make sure that letsencrypt dir exists, if not abort
cd /etc/letsencrypt/ || exit 1
sudo zip -r ../letsencryptdir.zip ../letsencrypt/

# Cleanup the extra copy of nginx.conf added to zip archive
rm /etc/letsencrypt/nginx.conf

# Sync with S3
cd /home/ubuntu
mv /etc/letsencryptdir.zip .
aws s3 cp letsencryptdir.zip "s3://${scpca_portal_cert_bucket}/"
rm letsencryptdir.zip
