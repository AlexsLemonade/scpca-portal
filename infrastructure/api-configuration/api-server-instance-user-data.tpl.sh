#!/bin/bash

# This is a template for the instance-user-data.sh script for the API Server.
# For more information on instance-user-data.sh scripts, see:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

# This script will be formatted by Terraform, which will read files from
# the project into terraform variables, and then template them into
# the following script. These will then be written out to files
# so that they can be used locally.

# Change to home directory of the default user
cd /home/ubuntu

# Install and configure Nginx.
cat <<"EOF" > nginx.conf
${nginx_config}
EOF
apt update -y
apt install nginx awscli zip -y
cp nginx.conf /etc/nginx/nginx.conf
service nginx restart

# Initialize crontab
sudo mkdir /var/log/cron
cat <<"EOF" >crontab.txt
${crontab_file}
EOF

crontab crontab.txt
rm crontab.txt

# Install and run docker
apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update -y
apt install docker-ce docker-ce-cli -y
sudo usermod -a -G docker ubuntu && newgrp docker

if [[ ${stage} == "staging" || ${stage} == "prod" ]]; then
  # Create and install SSL Certificate for the API.
  # Only necessary on staging and prod.
  # We cannot use ACM for this because *.bio is not a Top Level Domain that Route53 supports.
  # Certbot must be installed regardless of whether or not a cert is present because of the auto renewal cron job (see below).
  apt-get update
  apt install certbot python3-certbot-nginx -y

  # Write script which syncs cert with s3 remote store
  cat <<"EOF" > certbot_s3_sync.sh
${certbot_s3_sync_script}
EOF
  chmod +x ./certbot_s3_sync.sh

  # Write script responsible for certbot cert renewal
  cat <<"EOF" > certbot_renew_deploy_hook.sh
${certbot_renew_deploy_hook_script}
EOF
  chmod +x ./certbot_renew_deploy_hook.sh

  # Add certbot cert auto renewal entry to cron
  (crontab -l 2>/dev/null; echo "${certbot_crontab_entry}") | crontab -

    # Check here for the cert in S3, if present then pull it down from s3, if not then run certbot.
    if aws s3api head-object --bucket "${scpca_portal_cert_bucket}" --key letsencrypt.zip > /dev/null 2>&1; then
        aws s3 cp "s3://${scpca_portal_cert_bucket}/letsencrypt.zip" letsencrypt.zip
        unzip letsencrypt.zip -d /etc/
        mv /etc/letsencrypt/nginx.conf /etc/nginx/
        service nginx restart
        rm letsencrypt.zip
    else
  # The certbot challenge cannot be completed until the aws_lb_target_group_attachment resources are created.
        sleep 180
        BASE_URL="scpca.alexslemonade.org"
        PREFIX="api"
        if [[ ${stage} == "staging" ]]; then
          PREFIX="$PREFIX.staging"
        fi
        certbot --nginx -d $PREFIX.$BASE_URL -n --agree-tos --redirect -m ${slack_certbot_email}
        ./certbot_s3_sync.sh
    fi
fi

# Install, configure and launch our CloudWatch Logs agent
cat <<EOF >awslogs.json
{
    "agent": {
        "run_as_user": "root"
    },
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/nginx/access.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${nginx_access_log_stream}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/nginx/error.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${nginx_error_log_stream}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/cron/sync_batch_jobs.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${sync_batch_jobs_log_stream}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/cron/submit_pending.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${submit_pending_log_stream}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/cron/expire_user_datasets.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${expire_user_datasets_log_stream}",
                        "retention_in_days": 30
                    },
                    {
                        "file_path": "/var/log/cron/certbot_renew.log",
                        "log_group_name": "${log_group}",
                        "log_stream_name": "${certbot_renew_log_stream}",
                        "retention_in_days": 30
                    }
                ]
            }
        }
    }
}
EOF

wget https://amazoncloudwatch-agent-us-east-1.s3.us-east-1.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb
amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:awslogs.json

# Rotate the logs, delete after 3 days.
echo "
/var/log/nginx/error.log {
    missingok
    notifempty
    compress
    size 20k
    daily
    maxage 3
}" >> /etc/logrotate.conf
echo "
/var/log/nginx/access.log {
    missingok
    notifempty
    compress
    size 20k
    daily
    maxage 3
}" >> /etc/logrotate.conf
echo "
/var/log/cron/sync_batch_jobs.log {
    missingok
    notifempty
    compress
    size 20K
    daily
    maxage 3
}" >> /etc/logrotate.conf
echo "
/var/log/cron/submit_pending.log {
    missingok
    notifempty
    compress
    size 20K
    daily
    maxage 3
}" >> /etc/logrotate.conf
echo "
/var/log/cron/certbot_renew.log {
    missingok
    notifempty
    compress
    size 20K
    daily
    maxage 3
}" >> /etc/logrotate.conf

# Install our environment variables
cat <<"EOF" > environment
${api_environment}
EOF

# Install the script to run commands
cat <<"EOF" > run_command.sh
${run_command_script}
EOF

chmod +x ./run_command.sh

# Install the API startup script
cat <<"EOF" > start_api_with_migrations.sh
${start_api_with_migrations}
EOF

chmod +x ./start_api_with_migrations.sh

./start_api_with_migrations.sh

# Delete the cloudinit and syslog in production.
export STAGE=${stage}
if [[ $STAGE = *"prod"* ]]; then
    rm /var/log/cloud-init.log
    rm /var/log/cloud-init-output.log
    rm /var/log/syslog
fi
