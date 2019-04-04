# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.urls import path,include

import gsoc.views

admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {
            'cmspages': CMSSitemap,
        }
    }),
    path('post/<int:pk>/comment/', gsoc.views.add_comment_to_article, name='add_comment_to_article'),
    path('reply/<int:pk>/comment/', gsoc.views.add_reply_to_comment, name='add_reply_to_comment'),
]

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    url('accounts/', include('django.contrib.auth.urls')),
    url('accounts/register', gsoc.views.register_view, name='register')
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    url(r'^', include('cms.urls'))
)
# This is only needed when using runserver.
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        # For django versions before 2.0:
        url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
# Add upload proposal page and after-login check
urlpatterns += [
    url('after-login/', gsoc.views.after_login_view, name='after-login'),
    url('upload-proposal/', gsoc.views.upload_proposal_view, name='upload-proposal'),
    url('cancel_proposal_upload/', gsoc.views.cancel_proposal_upload_view, name='cancel-proposal-upload'),
]
