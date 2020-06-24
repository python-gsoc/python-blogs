# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.wizards.wizard_pool import wizard_pool
from cms.wizards.wizard_base import Wizard
from cms.wizards.forms import BaseFormMixin

from parler.forms import TranslatableModelForm
from treebeard.forms import movenodeform_factory, MoveNodeForm

from .models import Category


class CategoryWizard(Wizard):

    def get_success_url(self, *args, **kwargs):
        # Since categories do not have their own urls, return None so that
        # cms knows that it should just close the wizard window (reload
        # current page)
        return None


class CreateCategoryForm(BaseFormMixin, TranslatableModelForm, MoveNodeForm):
    """
    The model form for Category wizard.
    """

    class Meta:
        model = Category
        fields = ['name', 'slug', ]


aldryn_category_wizard = CategoryWizard(
    title=_('New category'),
    weight=290,
    form=movenodeform_factory(Category, form=CreateCategoryForm),
    description=_('Create a new category.')
)

wizard_pool.register(aldryn_category_wizard)
