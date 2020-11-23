# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_people.search_indexes import PeopleIndex

from . import BasePeopleTest
from ..models import Person


class TestPeopleIndex(BasePeopleTest):
    def test_get_title(self):
        idx_obj = PeopleIndex()
        person1 = self.reload(self.person1, "en")
        self.assertEqual(idx_obj.get_title(person1), person1.name)
        person1 = self.reload(self.person1, "de")
        self.assertEqual(idx_obj.get_title(person1), person1.name)

    def test_get_index_kwargs(self):
        # This is a silly test, but is here for completeness.
        idx_obj = PeopleIndex()
        self.assertEqual(idx_obj.get_index_kwargs("en"), {
            'translations__language_code': 'en'
        })

    def test_get_index_queryset(self):
        idx_obj = PeopleIndex()
        # Person2 does NOT have an EN translation, so should appear here.
        self.assertEqualItems(
            [q.id for q in idx_obj.get_index_queryset("en")],
            [self.person1.id],
        )
        # Both person objects have DE translations
        self.assertEqualItems(
            [q.id for q in idx_obj.get_index_queryset("de")],
            [self.person1.id, self.person2.id],
        )

    def test_get_model(self):
        # This is a silly test, but is here for completeness.
        idx_obj = PeopleIndex()
        self.assertEqual(idx_obj.get_model(), Person)

    def test_get_search_data(self):
        idx_obj = PeopleIndex()
        person1 = self.reload(self.person1, "en")
        search_data = idx_obj.get_search_data(person1, "en", None)
        self.assertEqual(search_data, self.data['person1']['en']['description'])
