import os
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from scpca_portal.config.common import Common
from scpca_portal.strtobool import strtobool


class Production(Common):
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    # Site.
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]

    UPDATE_S3_DATA = True

    # AWS S3
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-inputs"
    AWS_S3_OUTPUT_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

    # AWS Batch
    AWS_BATCH_FARGATE_JOB_QUEUE_NAME = os.environ.get("AWS_BATCH_FARGATE_JOB_QUEUE_NAME")
    AWS_BATCH_FARGATE_JOB_DEFINITION_NAME = os.environ.get("AWS_BATCH_FARGATE_JOB_DEFINITION_NAME")
    AWS_BATCH_EC2_JOB_QUEUE_NAME = os.environ.get("AWS_BATCH_EC2_JOB_QUEUE_NAME")
    AWS_BATCH_EC2_JOB_DEFINITION_NAME = os.environ.get("AWS_BATCH_EC2_JOB_DEFINITION_NAME")

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches
    # (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    AWS_HEADERS = {
        "Cache-Control": "max-age=86400, s-maxage=86400, must-revalidate",
    }

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("DATABASE_NAME"),
            "USER": os.getenv("DATABASE_USER"),
            "PASSWORD": os.getenv("DATABASE_PASSWORD"),
            "HOST": os.getenv("DATABASE_HOST"),
            "PORT": os.getenv("DATABASE_PORT"),
        }
    }

    PRODUCTION = True

    CLEAN_UP_DATA = True

    ENABLE_FEATURE_PREVIEW = strtobool(os.getenv("ENABLE_FEATURE_PREVIEW", "false"))

    SENTRY_DSN = os.getenv("SENTRY_DSN", None)

    if SENTRY_DSN == "None":
        SENTRY_DSN = None

    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            environment=os.getenv("SENTRY_ENV"),
            # If you wish to associate users to errors (assuming you are using
            # django.contrib.auth) you may enable sending PII data.
            send_default_pii=True,
        )

    # Code Paths
    INPUT_DATA_PATH = Path("/home/user/data/input")
    OUTPUT_DATA_PATH = Path("/home/user/data/output")
    README_PATH = Path("/home/user/data/readmes")
    TEMPLATE_PATH = Path("/home/user/scpca_portal/templates")
