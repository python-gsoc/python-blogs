# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from aldryn_people.views import DownloadVcardView, GroupDetailView, GroupListView, PersonDetailView


urlpatterns = [
    url(r'^group/(?P<pk>[0-9]+)/$',
        GroupDetailView.as_view(), name='group-detail'),
    url(r'^group/(?P<slug>[A-Za-z0-9_\-]+)/$',
        GroupDetailView.as_view(), name='group-detail'),

    url(r'^(?P<pk>[0-9]+)/$',
        PersonDetailView.as_view(), name='person-detail'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/$',
        PersonDetailView.as_view(), name='person-detail'),

    url(r'^(?P<pk>[0-9]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),
    url(r'^(?P<slug>[A-Za-z0-9_\-]+)/download/$',
        DownloadVcardView.as_view(), name='download_vcard'),

    url(r'^$',
        GroupListView.as_view(), name='group-list'),
]
