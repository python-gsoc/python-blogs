# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0016_person_fk_to_one_to_one'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name='email', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name='email', blank=True),
        ),
    ]
