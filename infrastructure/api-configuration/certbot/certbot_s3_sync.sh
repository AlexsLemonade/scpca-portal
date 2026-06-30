#!/bin/bash

# Build the archive with paths relative to /etc (letsencrypt/..., nginx/nginx.conf)
# so it restores cleanly with `unzip -d /etc/`. The subshell keeps the cd local.
# -y preserves certbot's live/ symlinks (otherwise renewal may break on restore).
(cd /etc && zip -r -y /home/ubuntu/letsencrypt.zip letsencrypt/ nginx/nginx.conf)

# Sync with S3
aws s3 cp /home/ubuntu/letsencrypt.zip "s3://${scpca_portal_cert_bucket}/"
rm /home/ubuntu/letsencrypt.zip
