# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from parler.utils.context import switch_language

from aldryn_categories.models import Category
from aldryn_categories.fields import (
    CategoryForeignKey,
    CategoryManyToManyField,
    CategoryModelChoiceField,
    CategoryMultipleChoiceField,
    CategoryOneToOneField,
)

from .base import CategoryTestCaseMixin


class TestCategoryField(CategoryTestCaseMixin, TestCase):

    def test_category_model_choice_field(self):
        root = Category.add_root(name="root")
        root.save()
        child1 = root.add_child(name="child1")
        child2 = root.add_child(name="child2")
        grandchild1 = child1.add_child(name="grandchild1")
        bad_grandchild = child1.add_child(
            name='bad grandchild<script>alert("bad stuff");</script>')
        field = CategoryModelChoiceField(None)

        self.assertEqual(
            field.label_from_instance(child2),
            "&nbsp;&nbsp;child2",
        )
        self.assertEqual(
            field.label_from_instance(grandchild1),
            "&nbsp;&nbsp;&nbsp;&nbsp;grandchild1",
        )
        self.assertEqual(
            field.label_from_instance(bad_grandchild),
            '&nbsp;&nbsp;&nbsp;&nbsp;bad grandchild&lt;script&gt;alert'
            '(&quot;bad stuff&quot;);&lt;/script&gt;',
        )

        # Tests that the field correctly throws an ImproperlyConfigured
        # exception if the given object is not a Category (or something that
        # acts like one)
        with self.assertRaises(ImproperlyConfigured):
            field.label_from_instance(object)

        # Check that using an untranslated language does not raise exceptions
        with switch_language(child1, 'it'):
            try:
                field.label_from_instance(child1)
            except ImproperlyConfigured:
                self.fail("Translating to an unavailable language should not "
                          "result in an exception.")

    def test_category_multiple_choice_field(self):
        root = Category.add_root(name="root")
        root.save()
        child1 = root.add_child(name="child1")
        child2 = root.add_child(name="child2")
        grandchild1 = child1.add_child(name="grandchild1")
        bad_grandchild = child1.add_child(
            name='bad grandchild<script>alert("bad stuff");</script>')
        root = self.reload(root)
        child1 = self.reload(child1)
        field = CategoryMultipleChoiceField(None)
        self.assertEqual(
            field.label_from_instance(child2),
            "&nbsp;&nbsp;child2",
        )
        self.assertEqual(
            field.label_from_instance(grandchild1),
            "&nbsp;&nbsp;&nbsp;&nbsp;grandchild1",
        )
        self.assertEqual(
            field.label_from_instance(bad_grandchild),
            '&nbsp;&nbsp;&nbsp;&nbsp;bad grandchild&lt;script&gt;alert'
            '(&quot;bad stuff&quot;);&lt;/script&gt;',
        )

        # Tests that the field correctly throws an ImproperlyConfigured
        # exception if the given object is not a Category (or something that
        # acts like one)
        with self.assertRaises(ImproperlyConfigured):
            field.label_from_instance(object)

        # Check that using an untranslated language does not raise exceptions
        with switch_language(child1, 'it'):
            try:
                field.label_from_instance(child1)
            except ImproperlyConfigured:
                self.fail("Translating to an unavailable language should not "
                          "result in an exception.")

    def test_category_fk_field(self):
        field = CategoryForeignKey(Category)
        form_field = field.formfield()
        self.assertTrue(isinstance(form_field, CategoryModelChoiceField))
        field_type = field.get_internal_type()
        self.assertEquals(field_type, 'ForeignKey')

    def test_category_one_to_one_field(self):
        field = CategoryOneToOneField(Category)
        form_field = field.formfield()
        self.assertTrue(isinstance(form_field, CategoryModelChoiceField))
        field_type = field.get_internal_type()
        self.assertEquals(field_type, 'ForeignKey')

    def test_category_many_to_many_field(self):
        field = CategoryManyToManyField(Category)
        form_field = field.formfield()
        self.assertTrue(isinstance(form_field, CategoryMultipleChoiceField))
        field_type = field.get_internal_type()
        self.assertEquals(field_type, 'ManyToManyField')
