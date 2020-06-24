# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.utils.translation import get_language_from_request
from django.views.generic import DetailView, ListView

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin

from aldryn_people.utils import get_valid_languages

from . import DEFAULT_APP_NAMESPACE
from .models import Group, Person


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang


class LanguageChangerMixin(object):
    """
    Convenience mixin that adds CMS Language Changer support.
    """
    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'object'):
            self.object = self.get_object()
        set_language_changer(request, self.object.get_absolute_url)
        return super(LanguageChangerMixin, self).get(request, *args, **kwargs)


class AllowPKsTooMixin(object):
    def get_object(self, queryset=None):
        """
        Bypass TranslatableSlugMixin if we are using PKs. You would only use
        this if you have a view that supports accessing the object by pk or
        by its translatable slug.

        NOTE: This should only be used on DetailViews and this mixin MUST be
        placed to the left of TranslatableSlugMixin. In fact, for best results,
        declare your view like this:

            MyView(…, AllowPKsTooMixin, TranslatableSlugMixin, DetailView):
        """
        if self.pk_url_kwarg in self.kwargs:
            return super(DetailView, self).get_object(queryset)

        # OK, just let Parler have its way with it.
        return super(AllowPKsTooMixin, self).get_object(queryset)


class DownloadVcardView(AllowPKsTooMixin, TranslatableSlugMixin, DetailView):
    model = Person

    def get(self, request, *args, **kwargs):
        person = self.get_object()
        if not person.vcard_enabled:
            raise Http404

        filename = "%s.vcf" % person.name
        vcard = person.get_vcard(request)
        try:
            vcard = vcard.decode('utf-8').encode('ISO-8859-1')
        except UnicodeError:
            pass
        response = HttpResponse(vcard, content_type="text/x-vCard")
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            filename)
        return response


class PersonDetailView(LanguageChangerMixin, AllowPKsTooMixin,
                       TranslatableSlugMixin, DetailView):
    model = Person


class GroupDetailView(LanguageChangerMixin, AllowPKsTooMixin,
                      TranslatableSlugMixin, DetailView):
    model = Group


class GroupListView(ListView):
    model = Group

    def dispatch(self, request, *args, **kwargs):
        self.request_language = get_language(request)
        self.request = request
        self.site_id = getattr(get_current_site(self.request), 'id', None)
        self.valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, self.request_language, self.site_id)
        return super(GroupListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(GroupListView, self).get_queryset()
        # prepare language properties for filtering
        return qs.translated(*self.valid_languages)

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        qs_ungrouped = Person.objects.filter(groups__isnull=True)
        context['ungrouped_people'] = qs_ungrouped.translated(
            *self.valid_languages)
        return context
