#!/usr/bin/env python
# encoding: utf-8

from django.db import models


class PushSubscription(models.Model):
    identifier = models.CharField(max_length=255, unique=True)

