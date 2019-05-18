from django.contrib.syndication.views import Feed

from gsoc.models import UserProfile, GsocYear

from aldryn_newsblog.cms_appconfig import NewsBlogConfig

from cms.models import Page


class BlogsFeed(Feed):
    title = "GSoC@PSF Blogs"
    link = '/blogs/'
    description = 'Updates on different student blogs of GSoC@PSF'

    def items(self):
        gsoc_year = GsocYear.objects.first()
        ups = UserProfile.objects.filter(role=3, gsoc_year=gsoc_year).all()
        pks = [_.app_config.pk for _ in ups]
        return NewsBlogConfig.objects.filter(pk__in=pks).all()

    def item_title(self, item):
        return item.app_title

    def item_link(self, item):
        p = Page.objects.get(application_namespace=item.namespace, publisher_is_draft=False)
        return p.get_absolute_url()
