# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import Http404
from django.test.client import RequestFactory
from django.urls import reverse

from cms.utils.i18n import force_language

from . import BasePeopleTest, CMSRequestBasedTest, DefaultApphookMixin
from ..views import DownloadVcardView


class TestDownloadVcardView(DefaultApphookMixin,
                            BasePeopleTest,
                            CMSRequestBasedTest):

    def test_as_view(self):
        """Tests that DownloadVcardView produces the correct headers."""
        person1 = self.reload(self.person1, "en")
        person1.slug = 'person1-slug'
        kwargs = {"slug": person1.slug}
        person1_url = reverse('aldryn_people:person-detail', kwargs=kwargs)
        factory = RequestFactory()
        request = factory.get(person1_url)
        response = DownloadVcardView.as_view()(request, **kwargs)
        filename = '{0}.vcf'.format(person1.name)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="{0}"'.format(filename)
        )
        # Now, disable vcards for this person, and re-test
        person1.vcard_enabled = False
        person1.save()
        with self.assertRaises(Http404):
            request = factory.get(person1_url)
            response = DownloadVcardView.as_view()(request, **kwargs)


class TestMainListView(BasePeopleTest, CMSRequestBasedTest):

    def test_list_view_with_only_en_apphook(self):
        page = self.create_apphook_page(multilang=False)
        # give some time for apphook reload middleware
        self.client.get(page.get_absolute_url())

        self.set_defalut_person_objects_current_language('en')
        with force_language('en'):
            url = page.get_absolute_url()
            person1_url = self.person1.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.person1.name)
        self.assertContains(response, person1_url)
        # should not contain person 2 since page for 'de' language is
        # not published
        self.assertNotContains(response, self.person2.name)
        self.assertNotContains(response, self.person2.slug)

    def test_list_view_with_en_and_de_apphook(self):
        page = self.create_apphook_page(multilang=True)
        # give some time for apphook reload middleware
        self.client.get(page.get_absolute_url())
        self.set_defalut_person_objects_current_language('en')
        with force_language('en'):
            url = page.get_absolute_url()
            person1_url = self.person1.get_absolute_url()
            person2_url = self.person2.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.person1.name)
        self.assertContains(response, self.person2.name)
        self.assertContains(response, person1_url)
        self.assertContains(response, person2_url)
