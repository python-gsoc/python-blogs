# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings

import djangocms_text_ckeditor.fields
import filer.fields.image
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filer', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.TextField(verbose_name='address', blank=True)),
                ('postal_code', models.CharField(max_length=20, verbose_name='postal code', blank=True)),
                ('city', models.CharField(max_length=255, verbose_name='city', blank=True)),
                ('phone', models.CharField(max_length=100, null=True, verbose_name='phone', blank=True)),
                ('fax', models.CharField(max_length=100, null=True, verbose_name='fax', blank=True)),
                ('email', models.EmailField(default='', max_length=75, verbose_name='email', blank=True)),
                ('website', models.URLField(null=True, verbose_name='website', blank=True)),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(verbose_name='description', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', editable=False, to='aldryn_people.Group', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'aldryn_people_group_translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeoplePlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('style', models.CharField(default='standard', max_length=50, verbose_name='Style', choices=[('standard', 'Standard'), ('feature', 'Feature')])),
                ('group_by_group', models.BooleanField(default=True, help_text='when checked, people are grouped by their group', verbose_name='group by group')),
                ('show_links', models.BooleanField(default=False, verbose_name='Show links to Detail Page')),
                ('show_vcard', models.BooleanField(default=False, verbose_name='Show links to download vCard')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('phone', models.CharField(max_length=100, null=True, verbose_name='phone', blank=True)),
                ('mobile', models.CharField(max_length=100, null=True, verbose_name='mobile', blank=True)),
                ('fax', models.CharField(max_length=100, null=True, verbose_name='fax', blank=True)),
                ('email', models.EmailField(default='', max_length=75, verbose_name='email', blank=True)),
                ('website', models.URLField(null=True, verbose_name='website', blank=True)),
                ('slug', models.CharField(max_length=255, unique=True, null=True, verbose_name='unique slug', blank=True)),
                ('vcard_enabled', models.BooleanField(default=True, verbose_name='enable vCard download')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, verbose_name='group', blank=True, to='aldryn_people.Group', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, null=True, blank=True, to=settings.AUTH_USER_MODEL, unique=True)),
                ('visual', filer.fields.image.FilerImageField(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='filer.Image', null=True)),
            ],
            options={
                'verbose_name': 'Person',
                'verbose_name_plural': 'People',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('function', models.CharField(default='', max_length=255, verbose_name='function', blank=True)),
                ('description', djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='Description', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', editable=False, to='aldryn_people.Person', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'aldryn_people_person_translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='persontranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='peopleplugin',
            name='people',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='aldryn_people.Person', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grouptranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
