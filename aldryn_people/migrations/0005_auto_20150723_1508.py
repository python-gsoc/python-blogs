# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0004_auto_20150622_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouptranslation',
            name='slug',
            field=models.SlugField(default='', max_length=255, verbose_name='slug'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='persons', verbose_name='group', blank=True, to='aldryn_people.Group', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='persons', null=True, blank=True, to=settings.AUTH_USER_MODEL, unique=True),
            preserve_default=True,
        ),
    ]
