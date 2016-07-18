#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'manifest/$', views.manifest, name='manifest'),

    url(r'^push/subscribe/$', views.subscribe, name='subscribe'),
    url(r'^push/unsubscribe/$', views.unsubscribe, name='unsubscribe'),

    url(r'^tracker/start/$', views.tracker_start, name='start'),
    url(r'^tracker/end/$', views.tracker_start, name='end'),

    url(r'^api/tracker/start/([a-zA-Z0-9\-_:]+)/', views.api_tracker_start, name='api-start'),
    url(r'^api/tracker/end/([a-zA-Z0-9\-_:]+)/', views.api_tracker_end, name='api-end'),

    url('^auth/login/$',
        auth_views.login,
        dict(template_name='auth/login.html'),
        name='login',
    ),
    url('^auth/logout/$',
        auth_views.logout,
        dict(next_page=settings.LOGIN_REDIRECT_URL),
        name='logout'
    ),
    url('^auth/signup/$', views.signup, name='signup'),
]
