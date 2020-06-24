# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0005_auto_20150723_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='groups',
            field=sortedm2m.fields.SortedManyToManyField(default=None, help_text='Choose and order the groups for this person, the first will be the "primary group".', related_name='people', to='aldryn_people.Group', blank=True),
            preserve_default=True,
        ),
    ]
