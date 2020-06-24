# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0008_remove_person_group'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['name'], 'verbose_name': 'Person', 'verbose_name_plural': 'People'},
        ),
        migrations.AddField(
            model_name='persontranslation',
            name='name',
            field=models.CharField(default='', help_text="Provide this person's name.", max_length=255, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='persontranslation',
            name='slug',
            field=models.SlugField(default='', help_text='Leave blank to auto-generate a unique slug.', max_length=255, verbose_name='slug'),
            preserve_default=True,
        ),
    ]
