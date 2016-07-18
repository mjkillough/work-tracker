#!/usr/bin/env python
# encoding: utf-8

import datetime
import unittest

import django.test
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.utils import timezone

import freezegun

from .. import models, tracker, views


class TrackerTestCase(django.test.TestCase):

    def setUp(self):
        super().setUp()
        self.user = auth.models.User.objects.create_user('username')

    def test_start_period(self):
        datetime = timezone.now()
        with freezegun.freeze_time(datetime):
            _period = tracker.start_period(self.user)
        period = models.Period.objects.get()
        self.assertEqual(period, _period)
        self.assertEqual(period.user, self.user)
        self.assertEqual(period.start, datetime)
        self.assertEqual(period.end, None)

    def test_end_period(self):
        start_datetime = timezone.now()
        models.Period.objects.create(user=self.user, start=start_datetime)
        end_datetime = start_datetime + datetime.timedelta(days=1)
        with freezegun.freeze_time(end_datetime):
            tracker.end_ongoing_periods(self.user)
        period = models.Period.objects.get()
        self.assertEqual(period.end, end_datetime)

    def test_end_multiple_periods(self):
        start_datetime = timezone.now()
        models.Period.objects.create(user=self.user, start=start_datetime)
        models.Period.objects.create(user=self.user, start=start_datetime)
        models.Period.objects.create(user=self.user, start=start_datetime)
        end_datetime = start_datetime + datetime.timedelta(days=1)
        with freezegun.freeze_time(end_datetime):
            tracker.end_ongoing_periods(self.user)
        periods = models.Period.objects.all()
        end_datetimes = [period.end for period in periods]
        self.assertEqual(end_datetimes, [end_datetime] * 3)

    def test_start_period_stops_ongoing(self):
        start_datetime1 = timezone.now()
        period1 = models.Period.objects.create(user=self.user, start=start_datetime1)
        start_datetime2 = start_datetime1 + datetime.timedelta(days=1)
        with freezegun.freeze_time(start_datetime2):
            period2 = tracker.start_period(self.user)
        self.assertEqual(period2.end, None)
        period1 = models.Period.objects.get(pk=period1.pk)
        self.assertEqual(period1.end, start_datetime2)

    def test_has_ongoing_period(self):
        start_datetime1 = timezone.now()
        period1 = models.Period.objects.create(user=self.user, start=start_datetime1)
        self.assertTrue(tracker.has_ongoing_period(self.user))


class TrackerViewsTestCase(django.test.TestCase):

    def setUp(self):
        super().setUp()
        self.factory = django.test.RequestFactory()
        self.user = auth.models.User.objects.create_user('username')

    def test_start(self):
        request = self.factory.post(reverse('start'))
        request.user = self.user
        with unittest.mock.patch.object(tracker, 'start_period') as mocked:
            views.tracker_start(request)
        mocked.assert_called_once_with(self.user)

    def test_end(self):
        request = self.factory.post(reverse('end'))
        request.user = self.user
        with unittest.mock.patch.object(tracker, 'end_ongoing_periods') as mocked:
            views.tracker_end(request)
        mocked.assert_called_once_with(self.user)
