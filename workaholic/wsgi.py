#!/usr/bin/env python
# encoding: utf-8

import os

from django.core.wsgi import get_wsgi_application

from whitenoise.django import DjangoWhiteNoise


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "workaholic.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
