import unicodedata

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import DefaultFeed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.template import RequestContext
from django.core.cache import cache
from django.http import HttpResponseNotFound

from gsoc.models import UserProfile, GsocYear

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.models import Article

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
    title = f"GSoC {gsoc_year} PSF Blogs"
    link = settings.INETLOCATION
    feed_url = f"{settings.INETLOCATION}/feed/"
    feed_type = CorrectMimeTypeFeed
    description = "Updates on different student blogs of GSoC@PSF"

    def get_object(self, request):
        page = int(request.GET.get('p', 1))
        articles_all = cache.get("articles_all")
        if articles_all is None:
            articles_all = list(Article.objects.order_by('-publishing_date').all())
            cache.set("articles_all", articles_all)
        count = len(articles_all)
        start_index = (page - 1) * 15
        end_index = page * 15
        articles = list(articles_all[start_index:end_index])
        return articles

    def items(self, obj):
        return obj

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
        return self.item_link(item)

    def item_guid_is_permalink(self, item):
        return True

    def item_link(self, item):
        site = Site.objects.first()
        section = item.app_config
        p = Page.objects.get(
            application_namespace=section.namespace, publisher_is_draft=False
        )
        url = "{}{}{}/".format(self.link, p.get_absolute_url(), item.slug, "/")
        return url
