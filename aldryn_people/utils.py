# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import NoReverseMatch, reverse

from cms.utils.i18n import force_language, get_language_object


def get_additional_styles():
    """
    Get additional styles choices from settings
    """
    styles = getattr(settings, 'PEOPLE_PLUGIN_STYLES', '')
    choices = [(s.strip().lower(), s.title()) for s in styles.split(',') if s]
    return choices


def is_valid_namespace(namespace):
    """
    Check if provided namespace has an app-hooked page.
    Returns True or False.
    """
    try:
        reverse('{0}:group-list'.format(namespace))
    except (NoReverseMatch, AttributeError):
        return False
    return True


def is_valid_namespace_for_language(namespace, language_code):
    """
    Check if provided namespace has an app-hooked page for given language_code.
    Returns True or False.
    """
    with force_language(language_code):
        return is_valid_namespace(namespace)


def get_valid_languages(namespace, language_code, site_id=None):
        langs = [language_code]
        if site_id is None:
            site_id = getattr(Site.objects.get_current(), 'pk', None)
        current_language = get_language_object(language_code, site_id)
        fallbacks = current_language.get('fallbacks', None)
        if fallbacks:
            langs += list(fallbacks)
        valid_translations = [
            lang_code for lang_code in langs
            if is_valid_namespace_for_language(namespace, lang_code)]
        return valid_translations
