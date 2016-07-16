#!/usr/bin/env python
# encoding: utf-8

from django.db import models
from django.contrib import auth


class PushSubscription(models.Model):
    user = models.ForeignKey(auth.models.User)
    identifier = models.CharField(max_length=255, unique=True)
