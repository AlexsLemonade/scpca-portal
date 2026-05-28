#!/bin/bash

LOG_FILE="/var/log/cron/certbot_renew.log"

echo "$(date): Cert renewed. Syncing cert with S3 and reloading Ngninx." >> "$LOG_FILE"

./certbot_s3_sync.sh --scpca-portal-cert-bucket ${scpca_portal_cert_bucket}

systemctl reload nginx
echo "$(date): Syncing complete and Nginx reloaded." >> "$LOG"
