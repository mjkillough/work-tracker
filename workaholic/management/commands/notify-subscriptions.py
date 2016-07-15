#!/usr/bin/env python
# encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from ... import push


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        push.notify_all_subscriptions()
