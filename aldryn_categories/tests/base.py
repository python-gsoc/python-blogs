# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random
import string

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from django.contrib.auth.models import User


class CategoryTestCaseMixin(object):
    """Mixin class for testing Categories"""

    @staticmethod
    def reload(node):
        """NOTE: django-treebeard requires nodes to be reloaded via the Django
        ORM once its sub-tree is modified for the API to work properly.

        See:: https://tabo.pe/projects/django-treebeard/docs/2.0/caveats.html

        This is a simple helper-method to do that."""
        return node.__class__.objects.get(id=node.id)

    @classmethod
    def rand_str(cls, prefix=u'', length=23, chars=string.ascii_letters):
        return prefix + u''.join(random.choice(chars) for _ in range(length))

    @classmethod
    def create_user(cls):
        return User.objects.create(
            username=cls.rand_str(), first_name=cls.rand_str(),
            last_name=cls.rand_str())

    @staticmethod
    def get_request(language=None):
        """
        Returns a Request instance populated with cms specific attributes.
        """
        request_factory = RequestFactory(HTTP_HOST=settings.ALLOWED_HOSTS[0])
        request = request_factory.get("/")
        request.session = {}
        request.LANGUAGE_CODE = language or settings.LANGUAGE_CODE
        # Needed for plugin rendering.
        request.current_page = None
        request.user = AnonymousUser()
        return request
