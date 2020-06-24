# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0002_auto_20150109_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorytranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'en', b'English'), (b'de', b'German'), (b'fr', b'French')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='categorytranslation',
            unique_together=set([('language_code', 'master'), ('language_code', 'slug')]),
        ),
    ]
