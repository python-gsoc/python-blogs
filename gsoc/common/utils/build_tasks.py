import json

from gsoc.models import UserProfile, GsocYear, BlogPostDueDate, Scheduler
from gsoc.common.utils.tools import build_send_mail_json


def build_pre_blog_reminders(builder):
    data = json.loads(builder.data)
    due_date = BlogPostDueDate.objects.get(pk=data['due_date_pk'])
    gsoc_year = GsocYear.objects.first()
    profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
    for profile in profiles:
        if profile.current_blog_count is not 0 and not (profile.hidden and
                                                        profile.reminder_disabled):
            template_data = {
                'current_blog_count': profile.current_blog_count,
                'due_date': due_date.date.strftime('%d %B %Y')
            }

            scheduler_data = build_send_mail_json(profile.user.email,
                                                  template='pre_blog_reminder.html',
                                                  subject='Reminder for Weekly Blog Post',
                                                  template_data=template_data)

            s = Scheduler.objects.create(command='send_email',
                                         data=scheduler_data)


def build_post_blog_reminders(builder):
    data = json.loads(builder.data)
    due_date = BlogPostDueDate.objects.get(pk=data['due_date_pk'])
    gsoc_year = GsocYear.objects.first()
    profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
    for profile in profiles:
        if profile.current_blog_count is not 0 and not (profile.hidden and
                                                        profile.reminder_disabled):
            student_template_data = {
                'current_blog_count': profile.current_blog_count,
                'due_date': due_date.date.strftime('%d %B %Y')
            }

            mentors_template_data = {
                'student_username': profile.user.username,
                'student_email': profile.user.email,
                'suborg_name': profile.suborg_full_name.suborg_name,
                'due_date': due_date.date.strftime('%d %B %Y'),
                'current_blog_count': profile.current_blog_count
            }

            suborg = profile.suborg_full_name
            mentors = UserProfile.objects.filter(suborg_full_name=suborg, role=2)
            suborg_admins = UserProfile.objects.filter(suborg_full_name=suborg, role=1)
            student_email = profile.user.email

            mentors_emails = [_.user.email for _ in mentors]
            mentors_emails.extend([_.user.email for _ in suborg_admins])

            scheduler_data_student = build_send_mail_json(
                student_email,
                template='post_blog_reminder_student.html',
                subject='Reminder for Weekly Blog Post',
                template_data=template_data
                )

            scheduler_data_mentors = build_send_mail_json(
                mentors_emails,
                template='post_blog_reminder_mentors.html',
                subject='Weekly Blog Post missed by a Student of your Sub-Org',
                template_data=template_data
                )

            Scheduler.objects.create(command='send_email',
                                     data=scheduler_data_student)

            Scheduler.objects.create(command='send_email',
                                     data=scheduler_data_mentors)
