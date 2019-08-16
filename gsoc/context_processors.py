from .settings import RECAPTCHA_PUBLIC_KEY


def recaptcha_site_key(request):
    return {"recaptcha_site_key": RECAPTCHA_PUBLIC_KEY}
