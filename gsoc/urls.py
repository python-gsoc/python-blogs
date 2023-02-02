# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from os import name

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

import gsoc.views
import gsoc.sitemaps as sitemaps

admin.autodiscover()

urlpatterns = [
    url(
        r"^sitemap.xml",
        sitemap,
        {"sitemaps": {"blog_sitemaps": sitemaps.BlogListSitemap}},
        ),
    url(
        r"^robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_file",
        ),
    url(r"^favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    ]

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    url("accounts/", include("django.contrib.auth.urls")),
    url("accounts/new", gsoc.views.new_account_view, name="new_account"),
    url("accounts/register", gsoc.views.register_view, name="register"),
    url("accounts/change_password", gsoc.views.change_password, name="change_password"),
    url("accounts/change_info", gsoc.views.change_info, name="change_info"),
    url("accounts/accept_invitation", gsoc.views.accept_invitation, name="accept_invitation"),
    ]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    url(r"^blogs/$", gsoc.views.redirect_blogs_list),
    url(r"^blogs/(?P<blog_name>[\w-]+)/$", gsoc.views.redirect_blogs),
    url(
        r"^blogs/(?P<blog_name>[\w-]+)/(?P<article_name>[\w-]+)/",
        gsoc.views.redirect_articles,
        ),
    url(r"^", include("cms.urls")),
    )
# This is only needed when using runserver.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns = (
        [
            url(
                r"^media/(?P<path>.*)$",
                serve,
                {"document_root": settings.MEDIA_ROOT, "show_indexes": True},
                )
            ]
        + staticfiles_urlpatterns()
        + urlpatterns
        )
# Add upload proposal page and after-login check
urlpatterns += [
    url("after-login/", gsoc.views.after_login_view, name="after-login"),
    url("upload-proposal/", gsoc.views.upload_proposal_view, name="upload-proposal"),
    url(
        "cancel_proposal_upload/",
        gsoc.views.cancel_proposal_upload_view,
        name="cancel-proposal-upload",
        ),
    url("confirm_proposal/", gsoc.views.confirm_proposal_view, name="confirm-proposal"),
    ]

# Add comment routes
urlpatterns += [
    url("comment/new/", gsoc.views.new_comment, name="new_comment"),
    url("comment/delete/", gsoc.views.delete_comment, name="delete_comment"),
    ]

# Review article routes
urlpatterns += [
    url(
        r"^article/review/(?P<article_id>[0-9]+)/",
        gsoc.views.review_article,
        name="review_article",
        ),
    url(
        r"^article/unpublish/(?P<article_id>[0-9]+)/",
        gsoc.views.unpublish_article,
        name="unpublish_article",
        ),
    url(
        r"^article/publish/(?P<article_id>[0-9]+)/",
        gsoc.views.publish_article,
        name="publish_article",
        ),
    ]

# Upload images
urlpatterns += [url(r"^upload/", gsoc.views.upload_file)]

# Readd user details
urlpatterns += [
    url(r"^readd/(?P<uuid>[\w-]+)/", gsoc.views.readd_users, name="readd_users")
    ]

urlpatterns += [url(r"^test/", gsoc.views.test, name="test")]

# Export routes
urlpatterns += [
    url("admin/export", gsoc.views.export_mentors, name="export_mentors"),
    url("export", gsoc.views.export_view, name="export_view")
    ]

# Google OAuth
urlpatterns += [
    url("authorize", gsoc.views.authorize, name="auth"),
    url("oauth2callback", gsoc.views.oauth2callback, name="oauth2callback")
    ]

# Review all articles at once
urlpatterns += [
    path(
        "mark_all_reviewed/<int:author_id>",
        gsoc.views.mark_all_article_as_reviewed,
        name="mark_all_reviewed"
        )
    ]
