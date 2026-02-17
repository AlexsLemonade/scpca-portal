import os
from pathlib import Path

import dj_database_url
from configurations import Configuration
from corsheaders.defaults import default_headers

from scpca_portal.strtobool import strtobool

BASE_DIR = Path(__file__).parent.parent


class Common(Configuration):
    INSTALLED_APPS = (
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third party apps
        "rest_framework",  # utilities for rest apis
        "django_filters",  # for filtering rest endpoints
        "django_extensions",  # additional management commands
        "drf_spectacular",  # OpenAPI 3.0
        "corsheaders",
        # Your apps
        "scpca_portal",
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = "scpca_portal.urls"
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    WSGI_APPLICATION = "scpca_portal.wsgi.application"

    ADMINS = (("Author", "ccdl@alexslemonade.org"),)

    # Postgres
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://postgres:@postgres:5432/postgres",
            conn_max_age=int(os.getenv("POSTGRES_CONN_MAX_AGE", 600)),
        )
    }

    # Caching: for now we're only caching a single record and its not
    # even intense to compute so the locally memory cache is
    # sufficient and memcache would be overkill.
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
            "TIMEOUT": None,
        }
    }

    # General.
    APPEND_SLASH = True
    TIME_ZONE = "UTC"
    LANGUAGE_CODE = "en-us"
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_TZ = True
    LOGIN_REDIRECT_URL = "/"

    # Static files (CSS, JavaScript, Images).
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = "/tmp/www/static/"
    STATICFILES_DIRS = []
    STATIC_URL = "/static/"
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )

    # Media files
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": STATICFILES_DIRS,
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety.
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

    # Indicates running in prod environment.
    PRODUCTION = False

    # Management commands should remove locally downloaded or created data.
    CLEAN_UP_DATA = False

    # Enable features before completed.
    # Use this to prevent certain areas from going to production.
    # By default this is enabled for local and tests.
    ENABLE_FEATURE_PREVIEW = True

    # Logging.
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
            "verbose": {
                "format": "%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s"
            },
            "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
        },
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
        },
        "handlers": {
            "django.server": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "propagate": True,
            },
            "django.server": {
                "handlers": ["django.server"],
                "level": "INFO",
                "propagate": False,
            },
            "django.request": {
                "handlers": ["mail_admins", "console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.db.backends": {"handlers": ["console"], "level": "INFO"},
        },
    }

    # Django
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    # Django Rest Framework.
    REST_FRAMEWORK = {
        # format is an attribute on some of our models, so it collides in the query param filtering
        "URL_FORMAT_OVERRIDE": None,
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": int(os.getenv("DJANGO_PAGINATION_LIMIT", 10)),
        "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ),
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        # 'SERVE_INCLUDE_SCHEMA': False,
    }

    # CORS - unrestricted.
    CORS_ORIGIN_ALLOW_ALL = True
    API_KEY_HEADER = "api-key"
    CORS_ALLOW_HEADERS = default_headers + (API_KEY_HEADER,)

    TERMS_AND_CONDITIONS = "PLACEHOLDER"

    # AWS
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    SLACK_NOTIFICATIONS_EMAIL = os.getenv("SLACK_NOTIFICATIONS_EMAIL")

    # EMAILS
    DOMAIN = os.getenv("AWS_SES_DOMAIN", "scpca.alexslemonade.org")
    EMAIL_SENDER = f"no-reply@{DOMAIN}"
    EMAIL_CONTACT_ADDRESS = "scpca@ccdatalab.org"  # Always here
    EMAIL_CHARSET = "UTF-8"

    # OpenAPI 3.0 - Swagger - Redoc
    # https://drf-spectacular.readthedocs.io/en/latest/settings.html
    SPECTACULAR_SETTINGS = {
        "SCHEMA_PATH_PREFIX": "/v[0-9]",
        "SERVE_INCLUDE_SCHEMA": False,
        "TITLE": "ScPCA Portal API",
        "DESCRIPTION": """
## Description
The Single-cell Pediatric Cancer Atlas is a collection of pediatric cancer projects
that collected single-cell sequencing data and were processed using the workflows
contained in https://github.com/AlexsLemonade/alsf-scpca.

#### Active Development
**NOTE**

We are currently working towards replacing downloading computed-files directly with new endpoints for downloading datasets.

There will be `ccdl-datasets` that closely match existing project computed files.

As well as `datasets` that are created and processed by API request.


#### Available Schema Views
- Swagger - [https://api.scpca.alexslemonade.org/docs/swagger](https://api.scpca.alexslemonade.org/docs/swagger/)
- ReDoc - [https://api.scpca.alexslemonade.org/docs/redoc](https://api.scpca.alexslemonade.org/docs/redoc/)

#### Questions/Feedback?

If you have a question or comment, please [file an issue on GitHub](https://github.com/AlexsLemonade/scpca-portal/issues) or send us an email at [requests@ccdatalab.org](mailto:requests@ccdatalab.org).
""",
        "TOS": "https://scpca.alexslemonade.org/terms-of-use",
        "CONTACT": {"email": "requests@ccdatalab.org"},
        "LICENSE": {"name": "BSD License"},
        "VERSION": "v1",
        "EXTERNAL_DOCS": {
            "description": "Additional documentation can be found at scpca.readthedocs.io",
            "url": "https://scpca.readthedocs.io/en/stable/",
        },
        "COMPONENT_NO_READ_ONLY_REQUIRED": True,
        "TAGS": [
            {
                "name": "tokens",
                "description": """Create and update API tokens.""",
            },
            {
                "name": "projects",
                "description": """List and view available projects.""",
            },
            {
                "name": "samples",
                "description": """List and view available samples.""",
            },
            {
                "name": "computed-files",
                "description": """List and view available downloadable computed-files.""",
            },
            {
                "name": "project-options",
                "description": """View a custom object that describes values for project list filtering.""",
            },
            {
                "name": "stats",
                "description": """Retrieve ScPCA Portal Stats.""",
            },
            # {
            #     "name": "ccdl-datasets",
            #     "description": """List, view, and get download_urls for pre-generated and managed datasets.""",
            # },
            # {
            #     "name": "datasets",
            #     "description": """Create, update, view, and get download_urls for pre-generated and managed datasets.""",
            # },
        ],
        # TODO: Once computed file is removed revisit
        "POSTPROCESSING_HOOKS": [],
        # "ENUM_NAME_OVERRIDES": {
        #     "CCDLDatasetFormatEnum": "scpca_portal.enums.DatasetFormats",
        # },
        # TODO: Update API header to be Authorization: Bearer <TokenID> and use built in support.
        "AUTHENTICATION_WHITELIST": [],
        "SECURITY": [
            {
                "APIKeyHeaderAuth": [],
            },
        ],
        "APPEND_COMPONENTS": {
            "securitySchemes": {
                "APIKeyHeaderAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "API-KEY",
                    "description": """Create an API Token below by adding your email address
                    and entering the Token ID in the form below to attach the api-key header to requests.
                    **Only activated tokens will work when passed.**""",
                }
            }
        },
    }
