# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0017_auto_20160109_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peopleplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, related_name='aldryn_people_peopleplugin', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
    ]
