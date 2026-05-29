#!/bin/bash

LOG_FILE="/var/log/cron/certbot_renew.log"

echo "$(date): Cert renewed. Syncing cert with S3 and reloading Ngninx." >> "$LOG_FILE"

./certbot_s3_sync.sh

systemctl reload nginx
echo "$(date): Syncing complete and Nginx reloaded." >> "$LOG"
