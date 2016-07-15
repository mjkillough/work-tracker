#!/usr/bin/env python
# encoding: utf-8

import json
import unittest.mock

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import django.test

from ..json import json_view


class JsonViewTestCase(django.test.TestCase):

    def setUp(self):
        super().setUp()
        self.factory = django.test.RequestFactory()
        resp = dict(success=True)
        self.dummy_view = unittest.mock.Mock(return_value=resp)
        self.dummy_view_resp_json = json.dumps(resp).encode('utf-8')

    def test_enforces_request_content_type(self):
        """Enforces `request.content_type=='application/json'` if `required_parameters!=[]`"""
        decorator = json_view(['key'])
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/', data=dict(key='value'))
        resp = wrapped_view(request)
        self.dummy_view.assert_not_called()
        self.assertIsInstance(resp, HttpResponseBadRequest)

    def test_no_parameters_with_request_missing_body(self):
        """"Does not require a `request.body` if `required_parameters=[]`"""
        decorator = json_view()
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/')
        resp = wrapped_view(request)
        self.dummy_view.assert_called_once_with(request)

    def test_no_parameters_with_request_body(self):
        """Allows a `request.body` if `required_parameters=[]`"""
        decorator = json_view()
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/',
            data=json.dumps(dict(key='value')),
            content_type='application/json'
        )
        resp = wrapped_view(request)
        self.dummy_view.assert_called_once_with(request)

    def test_missing_request_body(self):
        """Complains if `request.body` is missing and `required_parameters!=[]`"""
        decorator = json_view(['param'])
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/', content_type='application/json')
        resp = wrapped_view(request)
        self.dummy_view.assert_not_called()
        self.assertIsInstance(resp, HttpResponseBadRequest)

    def test_missing_parameter(self):
        """Complains if a required parameter is missing"""
        decorator = json_view(['param1', 'param2'])
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/',
            data=json.dumps(dict(param1=1)),
            content_type='application/json'
        )
        resp = wrapped_view(request)
        self.dummy_view.assert_not_called()
        self.assertIsInstance(resp, HttpResponseBadRequest)

    def test_too_many_parameters(self):
        """If a view receives more than its required parameters, then they
        should be passed as kwargs."""
        decorator = json_view(['param1'])
        wrapped_view = decorator(self.dummy_view)
        request = self.factory.post('/',
            data=json.dumps(dict(param1=1, param2=2)),
            content_type='application/json'
        )
        resp = wrapped_view(request)
        self.dummy_view.assert_called_once_with(request, 1, param2=2)

    def test_passes_through_httpresponse_from_view(self):
        """A HttpResponse returned from the view is passed through unchanged"""
        expected_resp = HttpResponse(1)
        view = unittest.mock.Mock(return_value=expected_resp)
        decorator = json_view()
        wrapped_view = decorator(view)
        request = self.factory.post('/')
        resp = wrapped_view(request)
        self.assertEqual(resp, expected_resp)

    def test_serializes_dict_from_view_as_json(self):
        """`dict()`s returned from the view are serialized as JSON"""
        json_dict = dict(success=True)
        view = unittest.mock.Mock(return_value=json_dict)
        decorator = json_view()
        wrapped_view = decorator(view)
        request = self.factory.post('/')
        resp = wrapped_view(request)
        self.assertIsInstance(resp, JsonResponse)
        self.assertEqual(resp.content, json.dumps(json_dict).encode('utf-8'))

    def test_view_returns_custom_httpresponse_subclass(self):
        """`HttpResponse` subclasses can be returned by the view to wrap the JSON"""
        json_dict = dict(success=True)
        view = unittest.mock.Mock(return_value=(HttpResponseBadRequest, json_dict))
        decorator = json_view()
        wrapped_view = decorator(view)
        request = self.factory.post('/')
        resp = wrapped_view(request)
        self.assertIsInstance(resp, HttpResponseBadRequest)
        self.assertEqual(resp.content, json.dumps(json_dict).encode('utf-8'))

    def test_exceptions_propogate(self):
        """Exceptions inside the view propogate out of the decorator [to middleware]"""
        view = unittest.mock.Mock(side_effect=KeyError())
        decorator = json_view()
        wrapped_view = decorator(view)
        request = self.factory.post('/')
        with self.assertRaises(KeyError):
            wrapped_view(request)
