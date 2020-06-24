# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grouptranslation',
            options={'default_permissions': (), 'verbose_name': 'Group Translation'},
        ),
        migrations.AlterModelOptions(
            name='persontranslation',
            options={'default_permissions': (), 'verbose_name': 'Person Translation'},
        ),
        migrations.AlterField(
            model_name='grouptranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='persontranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'en', b'English')]),
            preserve_default=True,
        ),
    ]
