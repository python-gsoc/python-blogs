# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('lft', models.PositiveIntegerField(db_index=True)),
                ('rgt', models.PositiveIntegerField(db_index=True)),
                ('tree_id', models.PositiveIntegerField(db_index=True)),
                ('depth', models.PositiveIntegerField(db_index=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'verbose_name': 'category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('language_code', models.CharField(max_length=15, choices=[('en', 'English')], verbose_name='Language', db_index=True)),
                ('name', models.CharField(default='', max_length=255, verbose_name='name')),
                ('slug', models.SlugField(max_length=255, verbose_name='slug', help_text='Provide a “slug” or leave blank for an automatically generated one.')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, editable=False, to='aldryn_categories.Category', null=True, related_name='translations')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'category Translation',
                'db_table': 'aldryn_categories_category_translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='categorytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
