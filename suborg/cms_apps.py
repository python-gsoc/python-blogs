from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class suborg(CMSApp):
    app_name = "suborg"
    name = _("Suborg")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["suborg.urls"]


apphook_pool.register(suborg)
