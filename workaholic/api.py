#!/usr/bin/env python
# encoding: utf-8

import collections
import functools

from django import http
from django.contrib import auth
from django.core import signing
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.utils.encoding import force_bytes

from .json import json_view


class BadApiKeySignature(Exception):
    pass

class ExpiredApiKey(Exception):
    pass


# We don't use `signing.loads`/`signing.dumps` because they use a timestamp
# which means the API key would change each time we issue it. This is
# undesirable. As we don't need to expire API keys, we can call `.sign` and
# `.unsign` directly.
_signer = signing.Signer(salt='api-key')
def _sign(obj):
    json = signing.JSONSerializer().dumps(obj)
    data = signing.b64_encode(json)
    return _signer.sign(data)
def _unsign(str):
    # Will raise `signing.BadSignature` for bad strings.
    data = force_bytes(_signer.unsign(str))
    json = signing.b64_decode(data)
    return signing.JSONSerializer().loads(json)


def _get_password_salt(user):
    password_parts = user.password.split('$')
    if len(password_parts) > 2:
        return password_parts[2]
    return ''


def get_api_key_for_user(user):
    # We include the user's password salt in the token so that the token is
    # invalidated when their password is changed. The salt is not secret.
    password_salt = _get_password_salt(user)

    # We use an OrderedDict to try and stop the API key changing. (It will
    # look very different if the order of the keys change).
    return _sign(collections.OrderedDict(
        user=user.id,
        salt=password_salt,
    ))


def get_user_for_api_key(key):
    try:
        json = _unsign(key)
    except signing.BadSignature:
        raise BadApiKeySignature
    user = auth.models.User.objects.get(id=json['user'])

    if _get_password_salt(user) != json['salt']:
        raise ExpiredApiKey

    return user


def endpoint(required_parameters=None):
    """View decorator which authorizes users using their API key

    Expects the urlconf to pass the API key as the first argument to the
    view. This decorator will authorize the key and supply the `.user`
    object on the view.

    This isn't very sophisticated. We just want to give users (me :)) some
    way of triggering the start/end of a Period using apps like Android's
    Trigger. These apps will allow you to open a URL, but not allow you
    to pass any data to it.
    """
    def decorator(view):
        @json_view(required_parameters)
        @functools.wraps(view)
        def wrapper(request, api_key, *args, **kwargs):
            try:
                request.user = get_user_for_api_key(api_key)
            except BadApiKeySignature:
                return (
                    http.HttpResponseBadRequest,
                    dict(success=False, error=_('Bad API key'))
                )
            except ExpiredApiKey:
                return (
                    http.HttpResponseBadRequest,
                    dict(success=False, error=_('API key expired'))
                )

            return view(request, *args, **kwargs)
        return wrapper
    return decorator

