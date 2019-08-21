import math
import unicodedata

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import DefaultFeed
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.template import RequestContext
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound

from gsoc.models import UserProfile, GsocYear

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.models import Article

from cms.models import Page, Site, Title
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


class BaseCorrectMimeTypeFeed(DefaultFeed):
    content_type = "application/xml; charset=utf-8"


class CorrectMimeTypeFeed(DefaultFeed):
    content_type = "application/xml; charset=utf-8"

    def add_root_elements(self, handler):
        super(CorrectMimeTypeFeed, self).add_root_elements(handler)
        if self.feed["page"] is not None:
            if not self.feed["show_all_articles"]:
                if (
                    self.feed["page"] >= 1
                    and self.feed["page"] <= self.feed["last_page"]
                ):
                    handler.addQuickElement(
                        "link",
                        "",
                        {
                            "rel": "first",
                            "href": f"{self.feed['feed_url']}?y={self.feed['year']}&p=1",
                        },
                    )
                    handler.addQuickElement(
                        "link",
                        "",
                        {
                            "rel": "last",
                            "href": (
                                f"{self.feed['feed_url']}?y={self.feed['year']}"
                                f"&p={self.feed['last_page']}"
                            ),
                        },
                    )
                    if self.feed["page"] > 1:
                        handler.addQuickElement(
                            "link",
                            "",
                            {
                                "rel": "previous",
                                "href": (
                                    f"{self.feed['feed_url']}?y={self.feed['year']}"
                                    f"&p={self.feed['page'] - 1}"
                                ),
                            },
                        )
                    if self.feed["page"] < self.feed["last_page"]:
                        handler.addQuickElement(
                            "link",
                            "",
                            {
                                "rel": "next",
                                "href": (
                                    f"{self.feed['feed_url']}?y={self.feed['year']}"
                                    f"&p={self.feed['page'] + 1}"
                                ),
                            },
                        )


class BlogsFeed(Feed):

    year = GsocYear.objects.first().gsoc_year
    title = f"GSoC {year} PSF Blogs"
    link = settings.INETLOCATION
    feed_type = CorrectMimeTypeFeed
    description = "Updates on different student blogs of GSoC@PSF"

    def get_object(self, request):
        year = int(request.GET.get("y", self.year))
        year_start = timezone.datetime(year, 1, 1)
        year_end = timezone.datetime(year, 12, 31)
        articles_all = list(
            Article.objects.filter(
                publishing_date__gte=year_start, publishing_date__lte=year_end
            )
            .order_by("-publishing_date")
            .all()
        )

        page = request.GET.get("p", 1)
        if page == "all":
            self.page = None
            self.last_page = None
            self.show_all_articles = True
            return articles_all

        self.show_all_articles = False
        self.page = int(page)
        count = len(articles_all)
        self.last_page = count < self.page * 15 and count >= (self.page - 1) * 15
        self.last_page = math.ceil(count / 15)
        start_index = (self.page - 1) * 15
        end_index = self.page * 15
        if self.page >= 1 and self.page <= self.last_page:
            articles = list(articles_all[start_index:end_index])
            return articles
        else:
            raise ObjectDoesNotExist

    def feed_extra_kwargs(self, obj):
        return {
            "page": self.page,
            "last_page": self.last_page,
            "show_all_articles": self.show_all_articles,
            "year": self.year,
        }

    def feed_url(self, obj):
        return f"{settings.INETLOCATION}/feed/?y={self.year}&p={self.page}"

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


class ArticlesFeed(Feed):

    year = GsocYear.objects.first().gsoc_year
    link = settings.INETLOCATION
    feed_type = BaseCorrectMimeTypeFeed

    def title(self):
        return f"Articles on {self.blog_title}"

    def description(self):
        return f"Updates on different articles published on {self.blog_title}"

    def feed_url(self, obj):
        return f"{settings.INETLOCATION}/en/feed/{self.blog_slug}/"

    def get_object(self, request, blog_slug):
        self.blog_slug = blog_slug
        page = Title.objects.get(slug=blog_slug, publisher_is_draft=False).page
        section = NewsBlogConfig.objects.get(namespace=page.application_namespace)
        self.blog_title = section.app_title
        articles = list(section.article_set.all())
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
