# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.utils.encoding import force_text

from cms import api
from cms.utils.i18n import force_language

from aldryn_people import DEFAULT_APP_NAMESPACE

from . import BasePeopleTest, DefaultApphookMixin
from ..cms_plugins import PeoplePlugin
from ..models import Group, Person


class TestPersonPlugins(DefaultApphookMixin, BasePeopleTest):

    def test_add_people_list_plugin_api(self):
        """
        We add a person to the People Plugin and look her up
        """
        name = 'Donald'
        Person.objects.create(name=name)
        plugin = api.add_plugin(self.placeholder, PeoplePlugin, self.language)
        plugin.people.set(Person.objects.all())
        self.assertEqual(force_text(plugin), force_text(plugin.pk))
        self.page.publish(self.language)

        url = self.page.get_absolute_url()
        response = self.client.get(url, follow=True)
        self.assertContains(response, name)

    # This fails because of Sane Add Plugin (I suspect). This will be refactored
    # and re-enabled in a future commit.
    # def test_add_people_list_plugin_client(self):
    #     """
    #     We log into the PeoplePlugin
    #     """
    #     self.client.login(
    #         username=self.su_username, password=self.su_password)
    #
    #     plugin_data = {
    #         'plugin_type': 'PeoplePlugin',
    #         'plugin_language': self.language,
    #         'placeholder_id': self.placeholder.pk,
    #     }
    #     response = self.client.post(URL_CMS_PLUGIN_ADD, plugin_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(CMSPlugin.objects.exists())

    def test_hide_ungrouped(self):
        """
        """
        the_bradys = Group.objects.create(name="The Bradys")
        alice = Person.objects.create(name="Alice")
        bobby = Person.objects.create(name="Bobby")
        cindy = Person.objects.create(name="Cindy")
        # Alice is the housekeeper, not a real Brady.
        bobby.groups.add(the_bradys)
        cindy.groups.add(the_bradys)

        # Add a plugin where ungrouped people are not shown
        plugin = api.add_plugin(self.placeholder, PeoplePlugin, self.language)
        plugin.people.set(Person.objects.all())
        plugin.group_by_group = True
        plugin.show_ungrouped = False
        plugin.save()

        self.page.publish(self.language)
        url = self.page.get_absolute_url()
        response = self.client.get(url, follow=True)
        self.assertContains(response, bobby.name)
        self.assertContains(response, cindy.name)
        self.assertNotContains(response, alice.name)

    def test_show_ungrouped(self):
        """
        """
        the_bradys = Group.objects.create(name="The Bradys")
        alice = Person.objects.create(name="Alice")
        bobby = Person.objects.create(name="Bobby")
        cindy = Person.objects.create(name="Cindy")
        # Alice is the housekeeper, not a real Brady.
        bobby.groups.add(the_bradys)
        cindy.groups.add(the_bradys)

        # Now, add a new plugin where ungrouped people are shown
        plugin = api.add_plugin(self.placeholder, PeoplePlugin, self.language)
        plugin.people.set(Person.objects.all())
        plugin.group_by_group = True
        plugin.show_ungrouped = True
        plugin.save()

        self.page.publish(self.language)
        url = self.page.get_absolute_url()
        response = self.client.get(url, follow=True)
        self.assertContains(response, bobby.name)
        self.assertContains(response, cindy.name)
        self.assertContains(response, alice.name)


class TestPeopleListPluginNoApphook(BasePeopleTest):

    def setUp(self):
        super(TestPeopleListPluginNoApphook, self).setUp()
        # we are testing only en
        self.person1.set_current_language('en')
        self.namespace = DEFAULT_APP_NAMESPACE

    def create_plugin(self, plugin_params=None):
        if plugin_params is None:
            plugin_params = {}
        with force_language('en'):
            plugin = api.add_plugin(
                self.placeholder, PeoplePlugin, 'en', **plugin_params)
            self.page.publish('en')
        return plugin

    def test_plugin_with_no_apphook_doesnot_breaks_page(self):
        self.create_plugin()
        url = self.page.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.person1.name)
        from ..cms_plugins import NAMESPACE_ERROR
        self.assertNotContains(response, NAMESPACE_ERROR[:20])

    def test_plugin_with_no_apphook_shows_error_message(self):
        self.create_plugin()
        url = self.page.get_absolute_url()
        self.client.login(username=self.su_username,
                          password=self.su_password)
        response = self.client.get(url, user=self.superuser)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.person1.name)
        from ..cms_plugins import NAMESPACE_ERROR
        self.assertContains(response, NAMESPACE_ERROR[:20])

    def test_plugin_with_vcard_enabled_no_apphook(self):
        self.create_plugin(plugin_params={'show_vcard': True})
        url = self.page.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, self.person1.name)

    def test_plugin_with_vcard_disabled_no_apphook(self):
        self.create_plugin(plugin_params={'show_vcard': False})
        url = self.page.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, self.person1.name)

    def test_plugin_show_links_are_shown_if_enabled_and_apphook_page(self):
        with force_language('en'):
            app_page = self.create_apphook_page()
            list_plugin = api.add_plugin(
                placeholder=self.placeholder,
                plugin_type=PeoplePlugin,
                language='en',
            )
            list_plugin.show_links = True
            list_plugin.save()
            self.page.publish('en')
            url = self.page.get_absolute_url()
            person_url = self.person1.get_absolute_url()
            # ensure that url is not the link to the home page and not app page
            app_page_len = len(app_page.get_absolute_url())
            self.assertGreater(len(person_url), app_page_len)
        response = self.client.get(url, follow=True)
        self.assertContains(response, person_url)
        # ensure that url is not shown if not enabled for plugin.
        list_plugin.show_links = False
        list_plugin.save()
        self.page.publish('en')
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, person_url)

    def test_plugin_with_vcard_enabled_with_apphook(self):
        vcard_kwargs = {
            'slug': self.person1.slug
        }
        with force_language('en'):
            self.create_apphook_page()
            person_vcard_url = reverse(
                '{0}:download_vcard'.format(self.namespace),
                kwargs=vcard_kwargs)
        plugin = self.create_plugin(plugin_params={'show_vcard': True})
        url = self.page.get_absolute_url()
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.person1.name)
        self.assertContains(response, person_vcard_url)
        # test that vcard download link is not shown if disabled
        plugin.show_vcard = False
        plugin.save()
        self.page.publish('en')
        response = self.client.get(url, follow=True)
        self.assertContains(response, self.person1.name)
        self.assertNotContains(response, person_vcard_url)
