# Generated by Django 3.2.13 on 2022-07-11 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gsoc', '0013_generator_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostduedate',
            name='generator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gsoc.generator'),
        ),
    ]
