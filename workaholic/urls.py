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
