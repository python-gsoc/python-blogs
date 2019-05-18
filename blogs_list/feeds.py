from django.contrib.syndication.views import Feed

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from cms.models import Page


class BlogsFeed(Feed):
    title = "GSoC@PSF Blogs"
    link = '/blogs/'
    description = 'Updates on different student blogs of GSoC@PSF'

    def items(self):
        return NewsBlogConfig.objects.all()

    def item_title(self, item):
        return item.app_title

    def item_link(self, item):
        p = Page.objects.get(application_namespace=item.namespace, publisher_is_draft=False)
        return p.get_absolute_url()
