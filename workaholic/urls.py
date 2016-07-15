#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'manifest/$', views.manifest, name='manifest'),

    url(r'^push/subscribe/$', views.subscribe, name='subscribe'),
    url(r'^push/unsubscribe/$', views.unsubscribe, name='unsubscribe'),
]
