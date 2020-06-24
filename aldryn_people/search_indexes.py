# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

from aldryn_search.utils import get_index_base, strip_tags

from .models import Person


class PeopleIndex(get_index_base()):
    haystack_use_for_indexing = getattr(settings, "ALDRYN_PEOPLE_SEARCH", True)

    INDEX_TITLE = True

    def get_title(self, obj):
        return obj.name

    def get_description(self, obj):
        return obj.description

    def get_index_kwargs(self, language):
        return {'translations__language_code': language}

    def get_index_queryset(self, language):
        return self.get_model().objects.active_translations(
            language_code=language).translated(language)

    def get_model(self):
        return Person

    def get_search_data(self, obj, language, request):
        return strip_tags(self.get_description(obj)).strip()
