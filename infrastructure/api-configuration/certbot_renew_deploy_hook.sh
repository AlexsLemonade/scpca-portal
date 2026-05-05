#!/bin/bash

SCPCA_PORTAL_CERT_BUCKET=${scpca_portal_cert_bucket}
LOG="/var/log/cron/certbot_renew.log"

echo "$(date): Cert renewed. Syncing cert with S3 and reloading Ngninx." >> "$LOG"

# Add the nginx.conf file that certbot setup to the zip dir.
cp /etc/nginx/nginx.conf /etc/letsencrypt/

cd /etc/ || exit
sudo zip -r letsencryptdir.zip letsencrypt/

# Cleanup the extra copy.
rm /etc/letsencrypt/nginx.conf

# Sync with S3
aws s3 cp letsencryptdir.zip "s3://$SCPCA_PORTAL_CERT_BUCKET/"
rm letsencryptdir.zip

systemctl reload nginx
echo "$(date): Syncing complete and Nginx reloaded." >> "$LOG"
