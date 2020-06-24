# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import aldryn_common.admin_fields.sortedm2m


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0014_auto_20150807_0033'),
    ]

    operations = [
        # Remove 'null=True' from the field definition: it has no effect.
        migrations.AlterField(
            model_name='peopleplugin',
            name='people',
            field=aldryn_common.admin_fields.sortedm2m.SortedM2MModelField(help_text='Select and arrange specific people, or, leave blank to select all.', to='aldryn_people.Person', blank=True),
        ),
    ]
