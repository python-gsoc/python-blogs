# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorytranslation',
            name='slug',
            field=models.SlugField(help_text='Provide a “slug” or leave blank for an automatically generated one.', blank=True, default='', verbose_name='slug', max_length=255),
            preserve_default=True,
        ),
    ]
