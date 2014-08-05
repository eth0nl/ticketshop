# Django production settings for ticketshop project.

from .base import *
from .secrets import *

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ticketshop',                      # Or path to database file if using sqlite3.
        'USER': 'ticketshop',                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': 'True',
    }
}

STATIC_ROOT = '/srv/static/ticketshop'
MEDIA_ROOT = '/srv/media/ticketshop'

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'https://35eb1915bd7c4208a70080d0bdcc5d94:%s@sentry.pyzuka.nl/3' % RAVEN_PASSWORD,
}

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('django_downloadview.nginx.XAccelRedirectMiddleware',)
DOWNLOADVIEW_BACKEND = 'django_downloadview.nginx.XAccelRedirectMiddleware'
WEASYPRINT_BASEURL = 'https://tickets.eth0.nl/'
