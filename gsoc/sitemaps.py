import urllib.parse

from django.contrib.sitemaps import Sitemap
from django.conf import settings

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.models import Article

from cms.models import Page


class BlogListSitemap(Sitemap):
    priority = 0.5

    def items(self):
        urls = ["/"]
        blogs = NewsBlogConfig.objects.all()
        for blog in blogs:
            try:
                p = Page.objects.get(
                    application_namespace=blog.namespace, publisher_is_draft=False
                )
                urls.append(p.get_absolute_url())
                articles = Article.objects.filter(app_config=blog).all()
                for i in range(len(articles) // 5):
                    urls.append(f"{p.get_absolute_url()}?page={i + 2}")
                for article in articles:
                    urls.append(f"{p.get_absolute_url()}{article.slug}/")
            except Exception as e:
                continue
        return urls

    def location(self, obj):
        return obj
