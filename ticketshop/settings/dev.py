# Django development settings for ticketshop project.

from .base import *

import os
import warnings
warnings.filterwarnings('error', r"DateTimeField received a naive datetime",
                        RuntimeWarning, r'django\.db\.models\.fields')

PROJECT_DIR = os.path.normpath(os.path.join(__file__, '../../..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'devticketshop',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'ATOMIC_REQUESTS': 'True',
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'trd$z*yswjz3gk$&hg^c@tp-d@h@75af^(6zse3$0yp!d++*w('

# Debug toolbar configuration
INSTALLED_APPS += (
    'debug_toolbar',
    'django_coverage',
)
MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES

DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS": False}
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
