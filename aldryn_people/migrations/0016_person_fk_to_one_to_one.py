# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0015_m2m_remove_null'),
    ]

    operations = [
        # Replace FK, 'unique=True' with OneToOneField.
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='persons', null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
