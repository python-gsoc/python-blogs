# Generated by Django 3.2.14 on 2022-08-05 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gsoc', '0018_rename_gsocenddatestandard_gsocenddatedefault'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gsocenddate',
            options={'verbose_name': 'Gsoc end date Max'},
        ),
        migrations.AlterField(
            model_name='builder',
            name='category',
            field=models.CharField(choices=[('build_pre_blog_reminders', 'build_pre_blog_reminders'), ('build_post_blog_reminders', 'build_post_blog_reminders'), ('build_revoke_student_perms', 'build_revoke_student_perms'), ('build_remove_user_details', 'build_remove_user_details'), ('build_add_timeline_to_calendar', 'build_add_timeline_to_calendar'), ('build_add_bpdd_to_calendar', 'build_add_bpdd_to_calendar'), ('build_add_event_to_calendar', 'build_add_event_to_calendar'), ('build_add_end_to_calendar', 'build_add_end_to_calendar'), ('build_add_end_standard_to_calendar', 'build_add_end_standard_to_calendar'), ('build_add_start_to_calendar', 'build_add_start_to_calendar'), ('build_mid_term_reminder', 'build_mid_term_reminder'), ('build_final_term_reminder', 'build_final_term_reminder')], max_length=40),
        ),
    ]
