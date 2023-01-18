# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import get_language_from_request, ugettext as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse

from parler.models import TranslatableModel
from six import iteritems

from .models import Group, Person


def get_obj_from_request(model, request,
                         pk_url_kwarg='pk',
                         slug_url_kwarg='slug',
                         slug_field='slug'):
    """
    Given a model and the request, try to extract and return an object
    from an available 'pk' or 'slug', or return None.

    Note that no checking is done that the view's kwargs really are for objects
    matching the provided model (how would it?) so use only where appropriate.
    """
    language = get_language_from_request(request, check_path=True)
    kwargs = request.resolver_match.kwargs
    mgr = model.objects
    if pk_url_kwarg in kwargs:
        return mgr.filter(pk=kwargs[pk_url_kwarg]).first()
    elif slug_url_kwarg in kwargs:
        # If the model is translatable, and the given slug is a translated
        # field, then find it the Parler way.
        filter_kwargs = {slug_field: kwargs[slug_url_kwarg]}
        translated_fields = model._parler_meta.get_translated_fields()
        if issubclass(model, TranslatableModel) and slug_url_kwarg in translated_fields:
            return mgr.active_translations(language, **filter_kwargs).first()
        else:
            # OK, do it the normal way.
            return mgr.filter(**filter_kwargs).first()
    else:
        return None


def get_admin_url(action, action_args=None, **url_args):
    """
    Convenience method for constructing admin-urls with GET parameters.
    """
    if action_args == None: 
        action_args = [] 
    base_url = admin_reverse(action, args=action_args)
    # Converts [{key: value}, …] => ["key=value", …]
    url_arg_list = sorted(iteritems(url_args))
    params = ["=".join([str(k), str(v)]) for (k, v) in url_arg_list]
    if params:
        return "?".join([base_url, "&".join(params)])
    else:
        return base_url


@toolbar_pool.register
class PeopleToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Person, Group, ]
    supported_apps = ('aldryn_people', )

    def populate(self):
        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            language = get_language_from_request(self.request, check_path=True)
            group = person = None
            if view_name == 'aldryn_people:group-detail':
                group = get_obj_from_request(Group, self.request)
            elif view_name in [
                    'aldryn_people:person-detail',
                    'aldryn_people:download_vcard']:
                person = get_obj_from_request(Person, self.request)
                if person and person.groups:
                    group = person.primary_group
            elif view_name in ['aldryn_people:group-list', ]:
                pass
            else:
                # We don't appear to be on any aldryn_people views so this
                # menu shouldn't even be here.
                return

            menu = self.toolbar.get_or_create_menu('people-app', "People")
            change_group_perm = user.has_perm('aldryn_people.change_group')
            add_group_perm = user.has_perm('aldryn_people.add_group')
            group_perms = [change_group_perm, add_group_perm]

            change_person_perm = user.has_perm('aldryn_people.change_person')
            add_person_perm = user.has_perm('aldryn_people.add_person')
            person_perms = [change_person_perm, add_person_perm]

            if change_group_perm:
                url = admin_reverse('aldryn_people_group_changelist')
                menu.add_sideframe_item(_('Group list'), url=url)

            if add_group_perm:
                url_args = {}
                if language:
                    url_args.update({"language": language})
                url = get_admin_url('aldryn_people_group_add', **url_args)
                menu.add_modal_item(_('Add new group'), url=url)

            if change_group_perm and group:
                url = get_admin_url('aldryn_people_group_change', [group.pk, ])
                menu.add_modal_item(_('Edit group'), url=url, active=True)

            if any(group_perms) and any(person_perms):
                menu.add_break()

            if change_person_perm:
                url = admin_reverse('aldryn_people_person_changelist')
                menu.add_sideframe_item(_('Person list'), url=url)

            if add_person_perm:
                url_args = {}
                if group:
                    url_args['groups'] = group.pk
                if language:
                    url_args['language'] = language
                url = get_admin_url('aldryn_people_person_add', **url_args)
                menu.add_modal_item(_('Add new person'), url=url)

            if change_person_perm and person:
                url = admin_reverse(
                    'aldryn_people_person_change', args=(person.pk, ))
                menu.add_modal_item(_('Edit person'), url=url, active=True)
