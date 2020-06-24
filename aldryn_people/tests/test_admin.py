# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from cms.utils.urlutils import admin_reverse

from . import BasePeopleTest
from ..admin import PersonAdmin


class TestPersonAdmin(BasePeopleTest):

    def test_all_translations(self):
        # Check that all the available languages appear in `all_translations`
        model_admin = PersonAdmin(self.person1, admin.site)
        all_translations = model_admin.all_translations(self.person1)
        obj_id = self.person1.id

        change_url = admin_reverse('aldryn_people_person_change', args=[obj_id])

        self.assertTrue(change_url + '?language=en' in all_translations)
        self.assertTrue(change_url + '?language=de' in all_translations)
        self.assertTrue(change_url + '?language=fr' in all_translations)
