# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import aldryn_common.admin_fields.sortedm2m


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0002_auto_20150128_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peopleplugin',
            name='people',
            field=aldryn_common.admin_fields.sortedm2m.SortedM2MModelField(help_text=None, to='aldryn_people.Person', null=True, blank=True),
            preserve_default=True,
        ),
    ]
