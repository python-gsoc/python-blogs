# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import defaultdict

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_people import DEFAULT_APP_NAMESPACE, models

from .utils import get_valid_languages


NAMESPACE_ERROR = _(
    "Seems that there is no valid application hook for aldryn-people."
    "Links can't be rendered without an app hook."
    )


class PeoplePlugin(CMSPluginBase):

    TEMPLATE_NAME = 'aldryn_people/plugins/%s/people_list.html'
    module = 'People'
    render_template = TEMPLATE_NAME % models.PeoplePlugin.STYLE_CHOICES[0][0]
    name = _('People list')
    model = models.PeoplePlugin

    fieldsets = (
        (None, {
            'fields': (
                'style',
                ),
            }),
        (_('People'), {
            'description': _('Select and arrange specific people, or leave '
                             'blank to use all.'),
            'fields': (
                'people',
                )
            }),
        (_('Options'), {
            'fields': (
                ('group_by_group', 'show_ungrouped', ),
                'show_links',
                'show_vcard',
                )
            })
        )

    def group_people(self, people):
        groups = defaultdict(list)

        for person in people:
            for group in person.groups.all():
                groups[group].append(person)

        # Fixes a template resolution-related issue. See:
        # http://stackoverflow.com/questions/4764110/django-template-cant-loop-defaultdict  # noqa
        groups.default_factory = None
        return groups

    def render(self, context, instance, placeholder):
        people = instance.get_selected_people()
        if not people:
            people = models.Person.objects.all()
        valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, instance.language, context['request'])
        people = people.translated(*valid_languages)
        if not valid_languages:
            context['namespace_error'] = NAMESPACE_ERROR
        self.render_template = self.TEMPLATE_NAME % instance.style

        context['instance'] = instance
        context['people'] = people

        if instance.group_by_group:
            context['people_groups'] = self.group_people(people)
            if instance.show_ungrouped:
                groupless = people.filter(groups__isnull=True)
            else:
                groupless = people.none()
            context['groupless_people'] = groupless
        else:
            context['people_groups'] = []
            context['groupless_people'] = people.none()
        return context


plugin_pool.register_plugin(PeoplePlugin)
