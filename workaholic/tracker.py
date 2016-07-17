#!/usr/bin/env python
# encoding: utf-8

import logging

from django.utils import timezone

from . import models

logger = logging.getLogger(__name__)


def get_ongoing_periods(user):
    ongoing_qs = models.Period.objects.filter(end=None)
    # There should be at most one Period in the QS. If something goes
    # really wrong, we might end up with multiple. It'd be nice if
    # we can add a constraint in the database to avoid this, but it
    # isn't obvious how we could do that.
    if ongoing_qs.count() > 1:
        logger.warn('User %s has %i on-going periods.', user, ongoing_qs.count())
    return ongoing_qs


def has_ongoing_period(user):
    return get_ongoing_periods(user).exists()


def end_ongoing_periods(user):
    ongoing_periods = get_ongoing_periods(user)
    for ongoing_period in ongoing_periods:
        ongoing_period.end = timezone.now()
        ongoing_period.save()


def start_period(user):
    # If the user already has an on-going period, end it now before starting a
    # new one. We do this because we probably missed the end of the previous
    # period. Recording them as two periods means the first can be edited to
    # have the correct end time.
    end_ongoing_periods(user)
    return models.Period.objects.create(
        user=user,
        start=timezone.now()
    )
