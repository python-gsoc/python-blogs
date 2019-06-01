from .settings import RECAPTCHA_PUBLIC_KEY


def recaptcha_site_key(request):
    return {
        'RECAPTCHA_SITE_KEY': RECAPTCHA_PUBLIC_KEY,
    }
