"""Настройки Django для проекта «Спортивные матчи» (вариант 9)."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-sport-matches-training-project-key'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'homepage',
    'courts',
    'matches',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'sport_matches.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'sport_matches.wsgi.application'
ASGI_APPLICATION = 'sport_matches.asgi.application'

# Django ORM не используется, поэтому база данных Django не настраивается.
# Данные читаются из SQLite через модуль sqlite3 (см. matches/db.py).
DATABASES = {}

MATCHES_DB_PATH = BASE_DIR / 'data' / 'matches.db'
SQL_QUERIES_PATH = BASE_DIR / 'sql' / 'queries.sql'

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = False

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        app_name: {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        }
        for app_name in ('homepage', 'courts', 'matches')
    },
}