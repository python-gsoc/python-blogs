import json

from django.utils import timezone

from gsoc.models import UserProfile, GsocYear, BlogPostDueDate, Scheduler
from gsoc.common.utils.tools import build_send_mail_json


def build_pre_blog_reminders(builder):
    try:
        data = json.loads(builder.data)
        due_date = BlogPostDueDate.objects.get(pk=data['due_date_pk'])
        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
        categories = (
            (0, 'Weekly Check-In'),
            (1, 'Blog Post'),
            )
        category = categories[due_date.category][1]
        for profile in profiles:
            if profile.current_blog_count is not 0 and not (profile.hidden or
                                                            profile.reminder_disabled):
                template_data = {
                    'current_blog_count': profile.current_blog_count,
                    'type': due_date.category,
                    'due_date': due_date.date.strftime('%d %B %Y')
                    }

                scheduler_data = build_send_mail_json(profile.user.email,
                                                      template='pre_blog_reminder.html',
                                                      subject=f'Reminder for {category}',
                                                      template_data=template_data)

                s = Scheduler.objects.create(command='send_email',
                                             data=scheduler_data)
        return None
    except Exception as e:
        return str(e)


def build_post_blog_reminders(builder):
    try:
        data = json.loads(builder.data)
        last_due_date = BlogPostDueDate.objects.last()
        due_date = BlogPostDueDate.objects.get(pk=data['due_date_pk'])
        if due_date == last_due_date:
            blogs_count = 0
        else:
            blogs_count = 1

        categories = (
            (0, 'Weekly Check-In'),
            (1, 'Blog Post'),
            )
        category = categories[due_date.category][1]

        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
        for profile in profiles:
            if profile.current_blog_count > blogs_count and not (profile.hidden or
                                                                 profile.reminder_disabled):
                suborg = profile.suborg_full_name
                mentors = UserProfile.objects.filter(suborg_full_name=suborg, role=2)
                suborg_admins = UserProfile.objects.filter(suborg_full_name=suborg, role=1)

                activation_date = builder.activation_date.date()

                if activation_date - due_date.date == timezone.timedelta(days=1):
                    student_template = 'first_post_blog_reminder_student.html'

                elif activation_date - due_date.date == timezone.timedelta(days=3):
                    student_template = 'second_post_blog_reminder_student.html'

                    mentors_emails = ['gsoc-admins@python.org']
                    mentors_emails.extend([_.user.email for _ in mentors])
                    mentors_emails.extend([_.user.email for _ in suborg_admins])

                    mentors_template_data = {
                        'student_username': profile.user.username,
                        'student_email': profile.user.email,
                        'suborg_name': profile.suborg_full_name.suborg_name,
                        'due_date': due_date.date.strftime('%d %B %Y'),
                        'current_blog_count': profile.current_blog_count
                        }

                    scheduler_data_mentors = build_send_mail_json(
                        mentors_emails,
                        template='post_blog_reminder_mentors.html',
                        subject=f'{category} missed by a Student of your Sub-Org',
                        template_data=mentors_template_data
                        )

                    Scheduler.objects.create(command='send_email',
                                             data=scheduler_data_mentors)

                student_template_data = {
                    'current_blog_count': profile.current_blog_count,
                    'due_date': due_date.date.strftime('%d %B %Y')
                    }

                scheduler_data_student = build_send_mail_json(
                    profile.user.email,
                    template=student_template,
                    subject=f'Reminder for {category}',
                    template_data=student_template_data
                    )

                Scheduler.objects.create(command='send_email',
                                         data=scheduler_data_student)
        return None
    except Exception as e:
        return str(e)


def build_revoke_student_perms(builder):
    try:
        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
        for profile in profiles:
            Scheduler.objects.create(command='revoke_student_permissions',
                                     data=profile.user.id)
    except Exception as e:
        return str(e)
