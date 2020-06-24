# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0003_auto_20150128_1359'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categorytranslation',
            options={'default_permissions': (), 'verbose_name': 'category Translation', 'managed': True},
        ),
        migrations.AlterField(
            model_name='categorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
    ]
