import os
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from scpca_portal.config.common import Common


class Production(Common):
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    # Site.
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]

    UPDATE_S3_DATA = True

    # AWS
    AWS_REGION = os.getenv("AWS_REGION")

    # AWS S3
    AWS_S3_INPUT_BUCKET_NAME = "scpca-portal-inputs"
    AWS_S3_OUTPUT_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

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
    CODE_PATH = Path("/home/user")

    DATA_PATH = CODE_PATH / "data"
    INPUT_DATA_PATH = DATA_PATH / "input"
    OUTPUT_DATA_PATH = DATA_PATH / "output"

    TEMPLATE_PATH = CODE_PATH / "scpca_portal" / "templates"
