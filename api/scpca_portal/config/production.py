import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from scpca_portal.config.common import Common


class Production(Common):
    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn",)

    # OAuth
    OAUTH_URL = os.getenv("OAUTH_URL")

    # AWS
    AWS_REGION = os.getenv("AWS_REGION")

    # AWS S3
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches (i.e. it is "public") for up to 1 day
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

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_IO_URL"),
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        environment=os.getenv("SENTRY_ENV"),
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
