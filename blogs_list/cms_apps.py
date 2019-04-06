from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class blogs_list(CMSApp):
    app_name = "blogs_list"
    name = _("Blogs")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["blogs_list.urls"]


apphook_pool.register(blogs_list)