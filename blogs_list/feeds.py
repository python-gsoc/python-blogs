import unicodedata

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import DefaultFeed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.template import RequestContext

from gsoc.models import UserProfile, GsocYear

from aldryn_newsblog.cms_appconfig import NewsBlogConfig

from cms.models import Page, Site
from cms.plugin_rendering import ContentRenderer


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")


def get_request(language=None):
    request_factory = RequestFactory()
    request = request_factory.get("/")
    request.session = {}
    request.LANGUAGE_CODE = language or settings.LANGUAGE_CODE

    # Needed for plugin rendering.
    request.current_page = None
    request.user = AnonymousUser()
    return request


class CorrectMimeTypeFeed(DefaultFeed):
    content_type = "application/xml; charset=utf-8"


class BlogsFeed(Feed):
    gsoc_year = GsocYear.objects.first()
    title = "GSoC "+str(gsoc_year)+" PSF Blogs"
    link = "/blogs/"
    feed_url = "/blogs/feed/"
    feed_type = CorrectMimeTypeFeed
    description = "Updates on different student blogs of GSoC@PSF"

    def items(self):
        gsoc_year = GsocYear.objects.first()
        ups = UserProfile.objects.filter(role=3, gsoc_year=gsoc_year).all()
        articles = []
        for up in ups:
            section = up.app_config
            articles.extend(list(section.article_set.all()))
        return articles

    def item_author_name(self, item):
        return item.owner.username

    def item_author_email(self, item):
        return item.owner.email

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if not item.lead_in:
            request = get_request()
            c = ContentRenderer(request)
            html = c.render_placeholder(item.content, RequestContext(request))
            return remove_control_characters(html)
        return item.lead_in

    def item_pubdate(self, item):
        return item.publishing_date

    def item_guid(self, item):
        site = Site.objects.first()
        return "https://{}{}".format(site.domain, self.item_link(item))

    def item_guid_is_permalink(self, item):
        return True

    def item_link(self, item):
        section = item.app_config
        p = Page.objects.get(
            application_namespace=section.namespace, publisher_is_draft=False
        )
        url = "{}{}/".format(p.get_absolute_url(), item.slug, "/")
        return url
