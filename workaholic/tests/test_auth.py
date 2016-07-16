#!/usr/bin/env python
# encoding: utf-8

import unittest

import django.test
from django.conf import settings
from django.contrib import auth
from django import http

from .. import forms, views


class AuthTestCase(django.test.TestCase):
    """Basic tests for our use of Django authentication

    We don't test much here, as Django has a very good test suite. We just
    want to test our use of it is correct."""

    LOGIN_URL = '/auth/login/'
    LOGOUT_URL = '/auth/logout/'
    SIGNUP_URL = '/auth/signup/'

    def setUp(self):
        super().setUp()
        self.client = django.test.Client()
        self.factory = django.test.RequestFactory()
        self.user = auth.models.User.objects.create_user('default_user')
        self.details = dict(
            username='username',
            password1='password',
            password2='password',
            email='receipient@example.com',
        )

    def test_index_redirects_to_login(self):
        """A non-authenticated user is redirected from / to login form.

        This test is not meant to test the precense of the `login_required`
        decorator. We really want to check that we've hooked up the django
        auth system (including `settings.LOGIN_URL`) correctly.
        """
        resp = self.client.get('/')
        self.assertRedirects(resp, self.LOGIN_URL + '?next=' + settings.LOGIN_REDIRECT_URL)

    def test_index_works_for_authenticated_user(self):
        """An authenticated user is not sent to the login form."""
        self.client.force_login(self.user)
        resp = self.client.get('/', follow=True)
        self.assertEqual(resp.redirect_chain, [])

    def test_signup_form_takes_email(self):
        """The sign up form requires e-mail and saves it to the model.

        We add this to `UserCreationForm`.
        """
        form = forms.SignupForm(dict())
        self.assertIn('email', form.errors)
        form = forms.SignupForm(dict(email='receipient@example.com'))
        self.assertNotIn('email', form.errors)

    def test_signup_form(self):
        """The sign up form creates the user and logs them in."""
        resp = self.client.post(self.SIGNUP_URL, self.details)
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_signup_form_takes_next(self):
        """The signup form redirects to the next= parameter on success"""
        self.details['next'] = '/?'
        resp = self.client.post(self.SIGNUP_URL, self.details)
        self.assertRedirects(resp, self.details['next'])

    def test_signup_form_sanitizes_next(self):
        """The signup form sanitizes next= to avoid absolute redirects"""
        self.details['next'] = '//example.com'
        resp = self.client.post(self.SIGNUP_URL, self.details)
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL) # not ['next']

    def test_signup_form_validates(self):
        """The signup view calls SignupForm.is_valid()"""
        request = self.factory.post(self.SIGNUP_URL, self.details)
        request.user = auth.models.AnonymousUser()
        with unittest.mock.patch.object(forms.SignupForm, 'is_valid', return_value=False) as mocked:
            resp = views.signup(request)
        mocked.assert_called_once_with()
        self.assertFalse(isinstance(resp, http.HttpResponseRedirect))

    def test_signup_form_redirects_when_already_logged_in(self):
        """An already logged in user can't see the Sign up form."""
        self.client.force_login(self.user)
        resp = self.client.get(self.SIGNUP_URL)
        self.assertRedirects(resp, settings.LOGIN_REDIRECT_URL)

    def test_logout_redirects(self):
        """Logout links logs the user out and redirects to login form"""
        self.client.force_login(self.user)
        resp = self.client.get(self.LOGOUT_URL, follow=True)
        self.assertRedirects(resp, self.LOGIN_URL + '?next=' + settings.LOGIN_REDIRECT_URL)
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated())
