import datetime
import sys
import logging
from pathlib import Path

import sentry_sdk
from decouple import config
from sentry_sdk.integrations.celery import CeleryIntegration as SentryCeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration as SentryDjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration as SentryLoggingIntegration


def str_split(value: str) -> list[str]:
    '''Splits a string by commas and returns a list of trimmed substrings.'''
    return [s.strip() for s in value.split(',')] if value else []


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Env variables
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOST', cast=str_split)
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=str_split)
LOG_DB_QUERIES = config('LOG_DB_QUERIES', cast=bool, default=False)
CACHE_STORAGE = config('CACHE_STORAGE')
USE_SENTRY = config('USE_SENTRY', cast=bool, default=False)

# Dialpad integration
SEND_DIALPAD_SMS = config('SEND_DIALPAD_SMS', cast=bool, default=False)
DIALPAD_API_TOKEN = config('DIALPAD_API_TOKEN', default='')


# Azure Blob
AZURE_STORAGE_ACCOUNT_SAS_TOKEN = config('AZ_SA_SAS_TOKEN', default='')
AZURE_STORAGE_ACCOUNT_NAME = config('AZ_SA_NAME', default='')
UPDATES_CONTAINER_NAME = config('AZ_SA_CT_NAME', default='')
UPDATES_PATH_PREFIX = config('UPDATES_PATH_PREFIX', default='daily_notification')

# Email
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": config('SENDGRID_API_KEY', default=''),
}
USE_DEBUG_EMAIL = config('USE_DEBUG_EMAIL', cast=bool, default=True)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='')
DEBUG_RECIPIENT = config('DEBUG_RECIPIENT', default='')
DEBUG_CC_RECIPIENT = config('DEBUG_CC_RECIPIENT', default='')

# User model
AUTH_USER_MODEL = 'apps.User'


# Application definition
INSTALLED_APPS = [
    # Default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # Project apps
    'apps',
    # Third-party apps
    'rest_framework',
    'drf_spectacular',
    'django_celery_results',
    'django_jsonform',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            Path(BASE_DIR, 'apps/admin/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST'),
        'PORT': config('POSTGRES_PORT'),
        # Connection pooling: 20-30% throughput increase
        'CONN_MAX_AGE': 600,  # Reuse connections for 10 minutes
        'CONN_HEALTH_CHECKS': True,  # Verify connection health before reuse
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_DIR = 'static'
STATIC_URL = f'/{STATIC_DIR}/'
STATIC_ROOT = BASE_DIR.joinpath(STATIC_DIR)

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}


# Media files
MEDIA_DIR = 'media'
MEDIA_URL = f'/{MEDIA_DIR}/'
MEDIA_ROOT = BASE_DIR.joinpath(MEDIA_DIR)


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Cache
DEFAULT_CACHE_DB = 'default'
CACHES = {
    DEFAULT_CACHE_DB: {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': CACHE_STORAGE,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}


# DRF
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ]
}


# JWT
ACCESS_TOKEN_LIFETIME = config('ACCESS_TOKEN_LIFETIME', cast=int)
REFRESH_TOKEN_LIFETIME = config('REFRESH_TOKEN_LIFETIME', cast=int)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(seconds=ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(seconds=REFRESH_TOKEN_LIFETIME),
    'ROTATE_REFRESH_TOKENS': True,
    'UPDATE_LAST_LOGIN': True,
    'USER_ID_FIELD': 'uuid',
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer',),
}


# Schema
SPECTACULAR_SETTINGS = {
    'TITLE': 'VetSuccess',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '%(asctime)s - [%(levelname)s] %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'libs': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

if LOG_DB_QUERIES:
    LOGGING['loggers']['django.db'] = {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': False,
    }

if USE_SENTRY:
    sentry_sdk.init(
        dsn=config('SENTRY_DSN', default=''),
        integrations=[
            SentryDjangoIntegration(),
            SentryCeleryIntegration(),
            SentryLoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
        ]
    )
