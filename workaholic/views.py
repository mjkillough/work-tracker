#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from . import models, push
from .json import json_view


def index(request):
    return render(request, 'main.html')


@json_view(['identifier'])
@require_http_methods(['POST'])
def subscribe(request, identifier):
    try:
        identifier = push.normalize_identifier(identifier)
    except push.BadIdentifierException as e:
        return HttpResponseBadRequest, dict(success=False, error=e.msg)
    # Be nice and allow the client app to tell us about the same
    # subscription more than once.
    models.PushSubscription.objects.get_or_create(identifier=identifier)
    return dict(success=True)


@json_view(['identifier'])
@require_http_methods(['POST'])
def unsubscribe(request, identifier):
    try:
        identifier = push.normalize_identifier(identifier)
        models.PushSubscription.objects.get(identifier=identifier).delete()
    except push.BadIdentifierException as e:
        return HttpResponseBadRequest, dict(success=False, error=e.msg)
    except models.PushSubscription.DoesNotExist:
        return HttpResponseBadRequest, dict(
            success=False, error='Subscription does not exist'
        )
    return dict(success=True)


@json_view()
def manifest(request):
    return dict(
        shortname='Workaholic',
        name='Workaholic',
        gcm_sender_id=settings.GCM_PROJECT_ID,
    )
