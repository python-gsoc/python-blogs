# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import aldryn_common.admin_fields.sortedm2m


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0011_auto_20150724_1900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='groups',
            field=aldryn_common.admin_fields.sortedm2m.SortedM2MModelField(default=None, help_text='Choose and order the groups for this person, the first will be the "primary group".', related_name='people', to='aldryn_people.Group', blank=True),
            preserve_default=True,
        ),
    ]
