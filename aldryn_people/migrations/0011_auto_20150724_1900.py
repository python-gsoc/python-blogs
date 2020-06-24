# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0010_auto_20150724_1654'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name': 'Person', 'verbose_name_plural': 'People'},
        ),
        migrations.RemoveField(
            model_name='person',
            name='name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='slug',
        ),
        migrations.AlterField(
            model_name='grouptranslation',
            name='name',
            field=models.CharField(help_text="Provide this group's name.", max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grouptranslation',
            name='slug',
            field=models.SlugField(default='', max_length=255, blank=True, help_text='Leave blank to auto-generate a unique slug.', verbose_name='slug'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='persontranslation',
            name='slug',
            field=models.SlugField(default='', max_length=255, blank=True, help_text='Leave blank to auto-generate a unique slug.', verbose_name='unique slug'),
            preserve_default=True,
        ),
    ]
