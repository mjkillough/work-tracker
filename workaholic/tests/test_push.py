#!/usr/bin/env python
# encoding: utf-8

import json
import django.test

from .. import views, models


class PushViewTests(django.test.TestCase):

    @staticmethod
    def _get_request(data):
        factory = django.test.RequestFactory()
        return factory.get(
            path='',
            data=data,
            content_type='application/json'
        )

    @staticmethod
    def _post_request(data):
        factory = django.test.RequestFactory()
        return factory.post(
            path='',
            data=json.dumps(data),
            content_type='application/json'
        )

    def test_subsribes(self):
        resp = views.subscribe(self._post_request(dict(identifier='a')))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf-8')), dict(success=True))
        self.assertEqual(models.PushSubscription.objects.filter(identifier='a').count(), 1)

    def test_resubscribe(self):
        resp1 = views.subscribe(self._post_request(dict(identifier='a')))
        resp2 = views.subscribe(self._post_request(dict(identifier='a')))
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(models.PushSubscription.objects.filter(identifier='a').count(), 1)

    def test_subscribes_requires_identifier(self):
        resp = views.subscribe(self._post_request(dict()))
        self.assertNotEqual(resp.status_code, 200)
        self.assertEqual(models.PushSubscription.objects.count(), 0)

    def test_subscribes_enforces_post(self):
        resp = views.subscribe(self._get_request(dict()))
        self.assertNotEqual(resp.status_code, 200)
        self.assertEqual(models.PushSubscription.objects.count(), 0)

    def test_unsubsribes(self):
        resp1 = views.subscribe(self._post_request(dict(identifier='a')))
        self.assertEqual(models.PushSubscription.objects.count(), 1)
        resp2 = views.unsubscribe(self._post_request(dict(identifier='a')))
        self.assertEqual(models.PushSubscription.objects.count(), 0)

    def test_unsubsribes_requires_identifier(self):
        resp = views.unsubscribe(self._post_request(dict()))
        self.assertNotEqual(resp.status_code, 200)

    def test_unsubscribes_enforces_post(self):
        resp = views.unsubscribe(self._get_request(dict()))
        self.assertNotEqual(resp.status_code, 200)
