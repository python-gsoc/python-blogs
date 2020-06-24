# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_text_ckeditor.fields
import aldryn_common.admin_fields.sortedm2m


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0013_peopleplugin_show_ungrouped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='peopleplugin',
            name='group_by_group',
            field=models.BooleanField(default=True, help_text='Group people by their group.', verbose_name='group by group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='peopleplugin',
            name='people',
            field=aldryn_common.admin_fields.sortedm2m.SortedM2MModelField(help_text='Select and arrange specific people, or, leave blank to select all.', to='aldryn_people.Person', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='peopleplugin',
            name='show_ungrouped',
            field=models.BooleanField(default=False, help_text='When using "group by group", show ungrouped people too.', verbose_name='show ungrouped'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='persontranslation',
            name='description',
            field=djangocms_text_ckeditor.fields.HTMLField(default='', verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='persontranslation',
            name='function',
            field=models.CharField(default='', max_length=255, verbose_name='role', blank=True),
            preserve_default=True,
        ),
    ]
