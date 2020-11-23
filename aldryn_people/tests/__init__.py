# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import clear_url_caches
from django.utils.translation import override

from cms import api
from cms.apphook_pool import apphook_pool
from cms.appresolver import clear_app_resolvers
from cms.exceptions import AppAlreadyRegistered
from cms.models import Page, Title
from cms.test_utils.testcases import BaseCMSTestCase
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import force_language, get_language_list

from djangocms_helper.utils import create_user

from ..models import Group, Person


APP_MODULE = 'aldryn_people.cms_apps'
DEFAULT_PEOPLE_NAMESPACE = 'aldryn_people'


class CleanUpMixin(object):

    def tearDown(self):
        self.reset_all()
        super(CleanUpMixin, self).tearDown()

    def reset_all(self):
        """
        Reset all that could leak from previous test to current/next test.
        :return: None
        """
        self.delete_app_module()
        self.reload_urls()
        self.apphook_clear()

    def delete_app_module(self):
        """
        Remove APP_MODULE from sys.modules. Taken from cms.
        :return: None
        """
        if APP_MODULE in sys.modules:
            del sys.modules[APP_MODULE]

    def apphook_clear(self):
        """
        Clean up apphook_pool and sys.modules. Taken from cms with slight
        adjustments and fixes.
        :return: None
        """
        try:
            apphooks = apphook_pool.get_apphooks()
        except AppAlreadyRegistered:
            # there is an issue with discover apps, or i'm using it wrong.
            # setting discovered to True solves it. Maybe that is due to import
            # from aldryn_events.cms_apps which registers EventListAppHook
            apphook_pool.discovered = True
            apphooks = apphook_pool.get_apphooks()

        for name, label in list(apphooks):
            if apphook_pool.apps[name].__class__.__module__ in sys.modules:
                del sys.modules[apphook_pool.apps[name].__class__.__module__]
        apphook_pool.clear()

    def reload_urls(self):
        """
        Clean up url related things (caches, app resolvers, modules).
        Taken from cms.
        :return: None
        """
        clear_app_resolvers()
        clear_url_caches()
        url_modules = [
            'cms.urls',
            'aldryn_events.urls',
            settings.ROOT_URLCONF
        ]

        for module in url_modules:
            if module in sys.modules:
                del sys.modules[module]


class DefaultApphookMixin(object):
    """
    Creates the default app hook page for aldryn-people. Relyes on
    BasePeopleTest.setUp method and its utilities.
    """

    def setUp(self):
        super(DefaultApphookMixin, self).setUp()
        self.app_hook_page = self.create_apphook_page(multilang=True)


class DefaultSetupMixin(object):
    su_username = 'user'
    su_password = 'pass'

    data = {
        'group1': {
            'en': {'name': 'group1', 'description': 'description1'},
            'de': {'name': 'Gruppe1', 'description': 'Beschreibung1'},
        },
        'group2': {
            # This should *not* have a EN translation
            'de': {'name': 'Gruppe2', 'description': 'Beschreibung2'},
        },
        'person1': {
            'en': {'name': 'person1', 'slug': 'person1',
                   'function': 'function1', 'description': 'description-en'},
            'de': {'name': 'mensch1', 'slug': 'mensch1',
                   'function': 'Funktion1', 'description': 'Beschreibung-de'},
        },
        'person2': {
            # This should *not* have a EN translation
            'de': {'name': 'mensch2', 'slug': 'mensch2',
                   'function': 'Funktion2', 'description': 'Beschreibung2'},
        },
    }

    def setUp(self):
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.page = api.create_page(
            'page', self.template, self.language, published=True)
        api.create_title('de', 'page de', self.page)
        self.page.publish('de')
        self.placeholder = self.page.placeholders.all()[0]
        self.superuser = self.create_superuser()
        super(DefaultSetupMixin, self).setUp()

    def create_superuser(self):
        return User.objects.create_superuser(
            self.su_username, 'email@example.com', self.su_password)

    def create_user(self, user_name, user_password, is_staff=False,
                    is_superuser=False):
        return User.objects.create(
            username=user_name,
            first_name='{0} first_name'.format(user_name),
            last_name='{0} last_name'.format(user_name),
            password=make_password(user_password),
            is_staff=is_staff,
            is_superuser=is_superuser
        )

    def create_apphook_page(self, multilang=False):
        with force_language('en'):
            page = api.create_page(
                title='People en', template=self.template, language='en',
                published=True,
                parent=self.page,
                apphook='PeopleApp',
                apphook_namespace=DEFAULT_PEOPLE_NAMESPACE,
            )
        page.publish('en')
        if multilang:
            api.create_title('de', 'People de', page)
            page.publish('de')
        return page.reload()


class BasePeopleTest(DefaultSetupMixin,
                     CleanUpMixin,
                     BaseCMSTestCase,
                     TestCase):

    @staticmethod
    def reload(obj, language=None):
        """Simple convenience method for re-fetching an object from the ORM,
        optionally "as" a specified language."""
        try:
            new_obj = obj.__class__.objects.language(language).get(id=obj.id)
        except obj.__class__.DoesNotExist:
            new_obj = obj.__class__.objects.get(id=obj.id)
        return new_obj

    def assertEqualItems(self, a, b):
        try:
            # In Python3, this method has been renamed (poorly)
            return self.assertCountEqual(a, b)
        except AttributeError:
            return self.assertItemsEqual(a, b)

    def mktranslation(self, obj, lang, **kwargs):
        """Simple method of adding a translation to an existing object."""
        try:
            obj.set_current_language(lang)
        except:  # noqa: This is a 3rd-party app, so we don't know for sure which kinds of errors may be raised here
            try:
                obj.translate(lang)
            except IntegrityError:
                pass
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()

    def setUp(self):
        super(BasePeopleTest, self).setUp()
        with override('en'):
            self.person1 = Person(**self.data['person1']['en'])
            self.group1 = Group(**self.data['group1']['en'])
        self.person1.name = 'person1'
        self.person1.slug = 'person1-slug'
        self.person1.save()
        self.group1.save()

        # Add a DE translation for person1, group1
        self.mktranslation(self.person1, 'de', **self.data['person1']['de'])
        self.mktranslation(self.group1, 'de', **self.data['group1']['de'])

        # Make person2, group2
        with override('de'):
            self.person2 = Person(**self.data['person2']['de'])
            self.group2 = Group(**self.data['group2']['de'])
        self.person2.save()
        self.group2.save()

        self.reset_all()

    def set_defalut_person_objects_current_language(self, language):
        """
        Make sure parler active language is set to language.
        :param language: language_code
        :return: None
        """
        self.person1.set_current_language(language)
        self.person2.set_current_language(language)


class CMSRequestBasedTest(CleanUpMixin, TestCase):
    """Sets-up User(s) and CMS Pages for testing."""
    languages = get_language_list()

    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory()
        cls.user = create_user('normal', 'normal@admin.com', 'normal')
        cls.site1 = Site.objects.get(pk=1)

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def get_or_create_page(self, base_title=None, languages=None):
        """Creates a page with a given title, or, if it already exists, just
        retrieves and returns it."""
        from cms.api import create_page, create_title
        if not base_title:
            # No title? Create one.
            base_title = self.rand_str(prefix="page", length=8)
        if not languages:
            # If no langs supplied, use'em all
            languages = self.languages
        # If there is already a page with this title, just return it.
        try:
            page_title = Title.objects.get(title=base_title)
            return page_title.page.get_draft_object()
        except (Title.DoesNotExist, Page.DoesNotExist):
            pass

        # No? Okay, create one.
        page = create_page(base_title, 'fullwidth.html', language=languages[0])
        # If there are multiple languages, create the translations
        if len(languages) > 1:
            for lang in languages[1:]:
                title_lang = "{0}-{1}".format(base_title, lang)
                create_title(language=lang, title=title_lang, page=page)
                page.publish(lang)
        return page.get_draft_object()

    def get_page_request(
            self, page, user, path=None, edit=False, lang_code='en'):
        from cms.middleware.toolbar import ToolbarMiddleware
        path = path or page and page.get_absolute_url()
        if edit:
            path += '?edit'
        request = RequestFactory().get(path)
        request.session = {}
        request.user = user
        request.LANGUAGE_CODE = lang_code
        if edit:
            request.GET = {'edit': None}
        else:
            request.GET = {'edit_off': None}
        request.current_page = page
        mid = ToolbarMiddleware()
        mid.process_request(request)
        return request
