#!/bin/bash

# Add the nginx.conf file that certbot setup to the zip dir.
cp /etc/nginx/nginx.conf /etc/letsencrypt/

# Make sure that letsencrypt dict exists, if not abort
cd /etc/letsencrypt/ || exit 1
sudo zip -r ../letsencryptdir.zip ../letsencrypt

# Cleanup the extra copy of nginx.conf added to zip archive
rm /etc/letsencrypt/nginx.conf

# Sync with S3
cd - || exit
mv /etc/letsencryptdir.zip .
aws s3 cp letsencryptdir.zip "s3://$SCPCA_PORTAL_CERT_BUCKET/"
rm letsencryptdir.zip
