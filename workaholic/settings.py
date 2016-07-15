#!/usr/bin/env python
# encoding: utf-8

import os

import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DJANGO_DEBUG') == 'true'
ALLOWED_HOSTS = [
    'workaholic.zvxrl.co.uk',
    'workaholic.herokuapp.com'
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

ROOT_URLCONF = 'workaholic.urls'
WSGI_APPLICATION = 'workaholic.wsgi.application'


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


GCM_URL = 'https://gcm-http.googleapis.com/gcm/send'
GCM_CHROME_IDENTIFIER_URL = 'https://android.googleapis.com/gcm/send/' # sent by browsers
GCM_API_KEY = os.environ['GCM_API_KEY']
GCM_PROJECT_ID = os.environ['GCM_PROJECT_ID']


INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'workaholic',
]


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]


DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}
