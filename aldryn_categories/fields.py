# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields.related import (
    ForeignKey,
    ManyToManyField,
    OneToOneField,
    CASCADE
)
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .models import Category


class CategoryLabelFromInstanceMixin(object):
    error_message = ''

    def label_from_instance(self, obj):
        prefix = ''
        try:
            if obj.depth > 1:
                prefix = '&nbsp;&nbsp;' * (obj.depth - 1)
            name = obj.safe_translation_getter('name')
            label = "{prefix}{name}".format(prefix=prefix, name=escape(name))
            return mark_safe(label)
        except AttributeError:
            raise ImproperlyConfigured(self.error_message)


class CategoryModelChoiceField(CategoryLabelFromInstanceMixin,
                               ModelChoiceField):
    """Displays choices hierarchically as per their position in the tree."""
    error_message = (
        "CategoryModelChoiceField should only be used for ForeignKey "
        "relations to the aldryn_categories.Category model.")


class CategoryForeignKey(ForeignKey):
    """
    Simply a normal ForeignKey field, but with a custom *default* form field
    which hierarchically displays the set of choices.
    """

    def __init__(self, to=Category, **kwargs):
        """Sets Category as the default `to` parameter."""
        kwargs['on_delete'] = getattr(kwargs, 'on_delete', CASCADE)
        super(CategoryForeignKey, self).__init__(to, **kwargs)

    # This is necessary for Django 1.7.4+
    def get_internal_type(self):
        return 'ForeignKey'

    def formfield(self, form_class=CategoryModelChoiceField,
                  choices_form_class=None, **kwargs):
        kwargs["form_class"] = form_class
        kwargs["choices_form_class"] = choices_form_class
        return super(CategoryForeignKey, self).formfield(**kwargs)


class CategoryOneToOneField(OneToOneField):
    """
    Simply a normal OneToOneField field, but with a custom *default* form field
    which hierarchically displays the set of choices.
    """

    def __init__(self, to=Category, **kwargs):
        """Sets Category as the default `to` parameter."""
        kwargs['on_delete'] = getattr(kwargs, 'on_delete', CASCADE)
        super(CategoryOneToOneField, self).__init__(to, **kwargs)

    # This is necessary for Django 1.7.4+
    def get_internal_type(self):
        return 'ForeignKey'

    def formfield(self, form_class=CategoryModelChoiceField,
                  choices_form_class=None, **kwargs):
        kwargs["form_class"] = form_class
        kwargs["choices_form_class"] = choices_form_class
        return super(OneToOneField, self).formfield(**kwargs)


class CategoryMultipleChoiceField(CategoryLabelFromInstanceMixin,
                                  ModelMultipleChoiceField):
    """Displays choices hierarchically as per their position in the tree."""
    error_message = (
        "CategoryMultipleChoiceField should only be used for M2M "
        "relations to the aldryn_categories.Category model.")


class CategoryManyToManyField(ManyToManyField):
    """
    Simply a normal ManyToManyField, but with a custom *default* form field
    which hierarchically displays the set of choices.
    """

    def __init__(self, to=Category, **kwargs):
        """Sets Category as the default `to` parameter."""
        super(CategoryManyToManyField, self).__init__(to, **kwargs)

    # This is necessary for Django 1.7.4+
    def get_internal_type(self):
        return 'ManyToManyField'

    def formfield(self, form_class=CategoryMultipleChoiceField,
                  choices_form_class=None, **kwargs):
        kwargs["form_class"] = form_class
        kwargs["choices_form_class"] = choices_form_class
        return super(CategoryManyToManyField, self).formfield(**kwargs)
