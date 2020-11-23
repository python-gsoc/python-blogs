# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.urls import reverse

from . import BasePeopleTest
from ..models import Person


class TestPersonAppHook(BasePeopleTest):

    def test_add_people_app(self):
        """
        We add a person to the app
        """
        self.page.application_urls = 'PeopleApp'
        self.page.application_namespace = 'aldryn_people'
        self.page.save()
        self.page.publish(self.language)

        person = Person.objects.create(
            name='Michael', phone='0785214521', email='michael@mit.ch',
            slug='michael'
        )
        # By slug
        url = reverse('aldryn_people:person-detail', kwargs={'slug': person.slug})
        response = self.client.get(url)
        self.assertContains(response, 'Michael')

        # By pk
        url = reverse('aldryn_people:person-detail', kwargs={'pk': person.pk})
        response = self.client.get(url)
        self.assertContains(response, 'Michael')
