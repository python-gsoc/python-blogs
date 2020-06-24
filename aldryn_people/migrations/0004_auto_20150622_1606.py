# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0003_auto_20150425_2103'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grouptranslation',
            options={'default_permissions': (), 'verbose_name': 'Group Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='persontranslation',
            options={'default_permissions': (), 'verbose_name': 'Person Translation', 'managed': True},
        ),
        migrations.AlterField(
            model_name='grouptranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='persontranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
    ]
