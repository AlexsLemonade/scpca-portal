#!/bin/bash

SCPCA_PORTAL_CERT_BUCKET=""

if [[ $# -eq 0 ]]; then
	echo "Error: Missing argument --scpca-portal-cert-bucket"
	exit 1
fi

case $1 in
	--scpca-portal-cert-bucket)
		SCPCA_PORTAL_CERT_BUCKET="$2"
		;;
	*)
		echo "Error: Unknown argument $1"
		echo "Acceptable arg: --scpca-portal-cert-bucket and --log-file-path"
		exit 1
		;;
esac

# Validate that value isn't empty
if [[ -z "$SCPCA_PORTAL_CERT_BUCKET" ]]; then
	echo "Error: No value provided for --scpca-portal-cert-bucket"
	exit 1
fi

# Add the nginx.conf file that certbot setup to the zip dir.
cp /etc/nginx/nginx.conf /etc/letsencrypt/

# Make sure that letsencrypt dict exists, if not abort
cd /etc/letsencrypt/ || exit 1
sudo zip -r ../letsencryptdir.zip ../letsencrypt/

# Cleanup the extra copy of nginx.conf added to zip archive
rm /etc/letsencrypt/nginx.conf

# Sync with S3
cd /home/ubuntu
mv /etc/letsencryptdir.zip .
aws s3 cp letsencryptdir.zip "s3://$SCPCA_PORTAL_CERT_BUCKET/"
rm letsencryptdir.zip
