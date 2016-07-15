#!/usr/bin/env python
# encoding: utf-8

import json
import functools

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.translation import gettext as _


def json_view(required_parameters=None):
    """Utility decorator for views which take/return JSON.

    It ensures that the body of the request is a JSON object with the
    keys given in `required_parameters`. It passes the values of these keys
    to the view function, in the order they are given in `required_parameters`.
    Any extra parameters are given as kwargs.
    Serializes the response from the view into JSON and returns as an
    `JsonResponse`. View functions should return a tupple of `(class, dict)`
    if they want us to wrap the JSON in a particular `HttpResponse` subclass.
    """
    if required_parameters is None:
        required_parameters = []

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):

            parameters = []
            json_parameters = {}
            if required_parameters:
                if request.META.get('CONTENT_TYPE', '') != 'application/json':
                    return HttpResponseBadRequest(json.dumps(dict(
                        success=False, error=_('Expected Content-Type of `application/json`')
                    )))
                # Grab the request body and ensure it has all of the keys
                # that we expect from `required_parameters`. Ignore extra parameters.
                json_parameters = json.loads(request.body.decode('utf-8'))
                for name in required_parameters:
                    if name not in json_parameters:
                        return HttpResponseBadRequest(json.dumps(dict(
                            success=False, error=_('Missing parameter: %s') % name
                        )))
                    parameters.append(json_parameters[name])
                    del json_parameters[name]

            # Execute the view. Pass through any parameters from `required_parameters`.
            # If the view returns a HttpResponse, assume it serialized the JSON itself.
            # Allow errors to propogate to middleware - this does mean that HTML responses
            # may be returned.
            resp = view_func(request, *parameters, *args, **kwargs, **json_parameters)
            if isinstance(resp, HttpResponse):
                return resp

            # If it returns a tuple, the first element will be the
            # HttpResponse subclass that should be used to wrap the JSON.
            # Otherwise, we'll use JsonResponse which does the serialization
            # for us.
            if isinstance(resp, tuple):
                resp_class, data = resp
                return resp_class(json.dumps(data), content_type='application/json')
            return JsonResponse(resp)
        return wrapper
    return decorator
