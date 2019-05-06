from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class SuborgForm(CMSApp):
    app_name = "suborg_form"
    name = _("Sub-org Submission")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["suborg_form.urls"]


apphook_pool.register(SuborgForm)
