#!/usr/bin/env python
# encoding: utf-8

import json
from django.conf import settings

import requests

from . import models


class BadIdentifierException(Exception):
    def __init__(self, msg):
        self.msg = msg


def normalize_identifier(identifier):
    """Takes an Push Subscription identifier from the browser and normalizes it.

    Google Chrome will give a GCM URL. We want to strip the generic part away,
    leaving just the identifier. If we don't get a GCM URL, raise an exception -
    we don't support talking to other Push services.
    """
    if not identifier.startswith(settings.GCM_CHROME_IDENTIFIER_URL):
        raise BadIdentifierException('Expected Google Cloud Messaging push subscription. Are you using Chrome?')
    return identifier[len(settings.GCM_CHROME_IDENTIFIER_URL):]


def notify_subscription(subscription):
    headers = {
        'Authorization': 'key=%s' % settings.GCM_API_KEY,
        'Content-Type': 'application/json'
    }
    data = json.dumps(dict(to=subscription.identifier))
    resp = requests.post(settings.GCM_URL, headers=headers, data=data)
    resp.raise_for_status()
    # TODO: Handle NotRegistered, which means we need to remove the subscription.


def notify_all_subscriptions():
    for subscription in models.PushSubscription.objects.all():
        notify_subscription(subscription)
