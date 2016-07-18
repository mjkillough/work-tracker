#!/usr/bin/env python
# encoding: utf-8

import json
import unittest

from django import http
import django.test
from django.contrib import auth

from .. import api


class ApiKeyTestCase(django.test.TestCase):

    def setUp(self):
        super().setUp()
        self.user = auth.models.User.objects.create_user('username', 'password')

    def test_api_key_stable(self):
        """A user's token should remain the same between requests"""
        token1 = api.get_api_key_for_user(self.user)
        token2 = api.get_api_key_for_user(self.user)
        self.assertEqual(token1, token2)

    def test_unsign_valid_token_returns_user(self):
        """We should be able to get a user back from their token"""
        token = api.get_api_key_for_user(self.user)
        user = api.get_user_for_api_key(token)
        self.assertEqual(user, self.user)

    def test_unsign_invalid_token(self):
        """We should throw an exception if someone mucks about with the token"""
        token = api.get_api_key_for_user(self.user)
        with self.assertRaises(api.BadApiKeySignature):
            api.get_user_for_api_key('a' + token)

    def test_changing_password_invalidates_key(self):
        """A token should be invalidated when the user changes their password"""
        token1 = api.get_api_key_for_user(self.user)
        self.user.set_password('password2')
        self.user.save()
        token2 = api.get_api_key_for_user(self.user)
        self.assertNotEqual(token1, token2)
        with self.assertRaises(api.ExpiredApiKey):
            api.get_user_for_api_key(token1)
        user = api.get_user_for_api_key(token2)
        self.assertEqual(user, self.user)


class ApiEndpointTestCase(django.test.TestCase):

    @unittest.mock.patch.object(
        api, 'get_user_for_api_key',
        side_effect=api.BadApiKeySignature
    )
    def test_invalid_token(self, mock):
        """The decorator should return an error if the API key is invalid"""
        view = unittest.mock.Mock()
        decorator = api.endpoint()
        decorated_view = decorator(view)
        resp = decorated_view(http.HttpRequest(), '')
        self.assertTrue(isinstance(resp, http.HttpResponseBadRequest))

    @unittest.mock.patch.object(
        api, 'get_user_for_api_key',
        side_effect=api.ExpiredApiKey
    )
    def test_expired_token(self, mock):
        """The decorator should return an error if the API key is expired"""
        view = unittest.mock.Mock()
        decorator = api.endpoint()
        decorated_view = decorator(view)
        resp = decorated_view(http.HttpRequest(), '')
        self.assertTrue(isinstance(resp, http.HttpResponseBadRequest))

    @unittest.mock.patch.object(
        api, 'get_user_for_api_key',
        return_value='not really a user'
    )
    def test_valid_token(self, mock):
        """The decorator should pass through the user to the view"""
        view = unittest.mock.Mock(return_value=dict())
        decorator = api.endpoint()
        decorated_view = decorator(view)
        resp = decorated_view(http.HttpRequest(), '')
        self.assertEqual(view.call_args[0][0].user, 'not really a user')
