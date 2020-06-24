# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, migrations


def forwards_func(apps, schema_editor):
    """
    These translation objects probably already exist, so, we need to carefully
    copy new field values into them.
    """
    Person = apps.get_model('aldryn_people', 'Person')
    PersonTranslation = apps.get_model('aldryn_people', 'PersonTranslation')

    for obj in Person.objects.all():
        PersonTranslation.objects.update_or_create(
            master_id=obj.pk,
            language_code=settings.LANGUAGE_CODE,
            defaults={
                "name": obj.name,
                "slug": obj.slug,
            }
        )


def backwards_func(apps, schema_editor):
    Person = apps.get_model('aldryn_people', 'Person')
    PersonTranslation = apps.get_model('aldryn_people', 'PersonTranslation')

    for obj in Person.objects.all():
        translation = _get_translation(obj, PersonTranslation)
        obj.name = translation.name
        obj.slug = translation.slug
        obj.save()


def _get_translation(object, MyModelTranslation):
    translations = MyModelTranslation.objects.filter(master_id=object.pk)
    try:
        # Try default translation
        return translations.get(language_code=settings.LANGUAGE_CODE)
    except ObjectDoesNotExist:
        try:
            # Try default language
            return translations.get(language_code=settings.PARLER_DEFAULT_LANGUAGE_CODE)
        except ObjectDoesNotExist:
            # Maybe the object was translated only in a specific language?
            # Hope there is a single translation
            return translations.get()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0009_auto_20150724_1654'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
