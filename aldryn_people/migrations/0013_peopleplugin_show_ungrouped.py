# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0012_auto_20150728_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='peopleplugin',
            name='show_ungrouped',
            field=models.BooleanField(default=False, help_text='when using "group by group", show ungrouped people too.', verbose_name='show ungrouped'),
            preserve_default=True,
        ),
    ]
