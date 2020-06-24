# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import six

from django.test import TestCase, TransactionTestCase
from django.utils import translation

from parler.utils.context import switch_language

from aldryn_categories.models import Category

from .base import CategoryTestCaseMixin


class TestCategories(CategoryTestCaseMixin, TransactionTestCase):
    """Implementation-specific tests"""

    def test_category_slug_creation(self):
        name = "Root Node"
        root = Category.add_root(name=name)
        root.set_current_language("en")
        root.save()
        self.assertEquals(root.slug, "root-node")

    def test_slug_collision(self):
        root = Category.add_root(name="test")
        root.save()
        root = self.reload(root)
        self.assertEquals(root.slug, "test")
        child1 = root.add_child(name="test")
        self.assertEquals(child1.slug, "test-1")
        child2 = root.add_child(name="test")
        self.assertEquals(child2.slug, "test-2")

    def test_str(self):
        root = Category.add_root(name="test")
        root.save()
        self.assertEqual(root.name, str(root))

    def test_str_malicious(self):
        malicious = "<script>alert('hi');</script>"
        escaped = "&lt;script&gt;alert(&#39;hi&#39;);&lt;/script&gt;"
        root = Category.add_root(name=malicious)
        root.save()
        self.assertEqual(six.u(str(root)), escaped)

    def test_delete(self):
        root = Category.add_root(name="test")
        root.save()
        child1 = root.add_child(name="Child 1")
        self.assertIn(child1, root.get_children())
        try:
            root.delete()
        except TypeError:
            self.fail('Deleting a node throws a TypeError.')
        except Exception:
            self.fail('Deleting a node throws an exception.')
        self.assertNotIn(child1, Category.objects.all())

    def test_non_ascii_slug_generation(self):
        """Test slug generation for common non-ASCII types of characters"""
        root = Category.add_root(name="Root Node")
        root.save()
        child1 = root.add_child(name="Germanic umlauts: ä ö ü ß Ä Ö Ü")
        self.assertEquals(child1.slug, "germanic-umlauts-a-o-u-ss-a-o-u")
        child2 = root.add_child(name="Slavic Cyrillic: смачні пляцки")
        self.assertEquals(child2.slug, "slavic-cyrillic-smachni-pliatski")
        child3 = root.add_child(name="Simplified Chinese: 美味蛋糕")
        self.assertEquals(child3.slug, "simplified-chinese-mei-wei-dan-gao")
        # non-ascii only slug
        child4 = root.add_child(name="ß ў 美")
        self.assertEquals(child4.slug, "ss-u-mei")


class TestCategoryTrees(CategoryTestCaseMixin, TestCase):
    """django-treebeard related tests"""

    def test_create_in_mem_category(self):
        name = "Root Node"
        root = Category.add_root(name=name)
        root.set_current_language("en")
        self.assertEquals(root.name, "Root Node")

    def test_create_in_orm_category(self):
        name = "Root Node"
        root = Category.add_root(name=name)
        root.set_current_language("en")
        root.save()
        root = self.reload(root)
        self.assertEquals(root.name, name)

    def test_tree_depth(self):
        a = Category.add_root(name="A")
        b = a.add_child(name="B")
        c = b.add_child(name="C")
        self.assertEqual(c.depth, 3)

    def test_get_children_count(self):
        a = Category.add_root(name="A")
        a.add_child(name="B")
        self.assertEquals(a.get_children_count(), 1)
        a.add_child(name="C")
        a = self.reload(a)
        self.assertEquals(a.get_children_count(), 2)

    def test_get_children(self):
        a = Category.add_root(name="A")
        b = a.add_child(name="B")
        self.assertIn(b, a.get_children())
        c = a.add_child(name="C")
        a = self.reload(a)
        self.assertIn(c, a.get_children())

    def test_get_descendants(self):
        a = Category.add_root(name="A")
        b = a.add_child(name="B")
        c = b.add_child(name="C")
        self.assertIn(c, a.get_descendants())
        d = b.add_child(name='D')
        b = self.reload(b)
        self.assertIn(d, b.get_descendants())

    def test_get_ancestors(self):
        a = Category.add_root(name="A")
        b = a.add_child(name="B")
        c = b.add_child(name="C")
        self.assertIn(a, b.get_ancestors())
        self.assertIn(a, c.get_ancestors())
        d = b.add_child(name='D')
        self.assertIn(a, d.get_ancestors())

    def test_move_category(self):
        a = Category.add_root(name="A")
        b = a.add_child(name="B")
        c = a.add_child(name="C")
        a = self.reload(a)
        b = self.reload(b)
        self.assertEqual(a, c.get_parent())
        self.assertNotEqual(b, c.get_parent())
        c.move(b, "first-child")
        b = self.reload(b)
        c = self.reload(c)
        self.assertEqual(b, c.get_parent())


class TestCategoryParler(CategoryTestCaseMixin, TestCase):
    """django-parler related tests"""

    def test_add_translations(self):
        values = [
            # language code, name, slug
            ('en', "Cheese Omelette", "cheese-omelette"),
            ('de', "Käseomelett", "kaseomelett"),
            ('fr', "Omelette au Fromage", "omelette-au-fromage"),
        ]

        node = None

        # Create the translations
        for lang, name, slug in values:
            if node:
                with switch_language(node, lang):
                    node.name = name
                    node.save()
            else:
                with translation.override(lang):
                    node = Category.add_root(name=name)
                    node.save()

        # Now test that they exist (and didn't obliterate one another)
        for lang, name, slug in values:
            with switch_language(node, lang):
                self.assertEqual(node.name, name)
                self.assertEqual(node.slug, slug)

        # Now test that we gracefully handle languages where there is no
        # translation.
        with switch_language(node, 'it'):
            try:
                node.name
            except Exception:
                self.fail("Translating to an unavailable language should not "
                          "result in an exception.")
