PORT=8081
DJANGO_CONFIGURATION=Production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=${django_secret_key}
DATABASE_HOST=${database_host}
DATABASE_PORT=${database_port}
DATABASE_USER=${database_user}
DATABASE_NAME=${database_name}
DATABASE_PASSWORD=${database_password}
# TODO: enable batch
# AWS_BATCH_JOB_QUEUE_NAME
# AWS_BATCH_JOB_DEFINITION_NAME
AWS_REGION=${aws_region}
AWS_S3_BUCKET_NAME=${aws_s3_bucket_name}
SENTRY_DSN=${sentry_dsn}
SENTRY_ENV=${sentry_env}
