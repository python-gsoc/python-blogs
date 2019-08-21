from aldryn_newsblog.cms_appconfig import NewsBlogConfig

from cms.models import Title, Page

from django.urls import reverse

from .settings import RECAPTCHA_PUBLIC_KEY


def recaptcha_site_key(request):
    return {"recaptcha_site_key": RECAPTCHA_PUBLIC_KEY}


def blog_slug(request):
    if hasattr(request, "current_app"):
        namespace = request.current_app
        try:
            page = Page.objects.get(
                application_namespace=namespace, publisher_is_draft=False
            )
            slug = Title.objects.get(page=page).slug
            feed_url = reverse("blogs_list:blog_feed", kwargs={"blog_slug": slug})
            return {"feed_url": feed_url}
        except Exception as e:
            return {}
    return {}
