# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def fk_to_m2m(apps, schema_editor):
    """
    Migrates any existing `group` to be the new, m2m `groups`
    """
    Person = apps.get_model("aldryn_people", "Person")
    for person in Person.objects.all():
        if person.group:
            person.groups.add(person.group)
            person.save()


def m2m_to_fk(apps, schema_editor):
    """
    Migrates any the first of any `groups` to be the `group`
    """
    Person = apps.get_model("aldryn_people", "Person")
    for person in Person.objects.all():
        group = person.groups.first()
        if group:
            person.group = group
            person.save()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0006_person_groups'),
    ]

    operations = [
        migrations.RunPython(fk_to_m2m, m2m_to_fk),
    ]
