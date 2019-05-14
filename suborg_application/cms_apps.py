from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class suborg_application(CMSApp):
    app_name = "suborg_application"
    name = _("Suborg Application")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["suborg_application.urls"]


apphook_pool.register(suborg_application)
