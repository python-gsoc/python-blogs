import json

from gsoc.models import UserProfile, GsocYear, BlogPostDueDate, Scheduler
from gsoc.common.utils.tools import build_send_mail_json


def build_pre_blog_reminders(builder):
    data = json.loads(builder.data)
    due_date = BlogPostDueDate.objects.get(pk=data['due_date_pk'])
    gsoc_year = GsocYear.objects.first()
    profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
    for profile in profiles:
        if profile.current_blog_count is not 0:
            template_data = {
                'current_blog_count': profile.current_blog_count,
                'due_date': due_date.date
            }

            scheduler_data = build_send_mail_json(profile.user.email,
                                                  template='pre_blog_reminder.html',
                                                  subject='Reminder for Weekly Blog Post',
                                                  template_data=template_data)

            s = Scheduler.objects.create(command='send_email',
                                         data=scheduler_data)
