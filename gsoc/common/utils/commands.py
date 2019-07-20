import json
from smtplib import SMTPResponseException, SMTPSenderRefused

from django.contrib.auth.models import User, Permission
from django.conf import settings

from .irc import send_message

from gsoc.models import (Scheduler, RegLink, GsocYear, UserProfile, Event,
                         BlogPostDueDate, SubOrgDetails)
from .tools import (send_mail, render_site_template, push_site_template,
                    archive_current_gsoc_files)


def send_email(scheduler: Scheduler):
    data = json.loads(scheduler.data)
    try:
        send_mail(data['send_to'],
                  data['subject'],
                  data['template'],
                  data['template_data'])
    except SMTPSenderRefused as e:
        last_error = json.dumps({
            "message": str(e),
            "smtp_code": e.smtp_code,
            })
        scheduler.last_error = last_error
        scheduler.success = False
        scheduler.save()
        return str(e)
    except SMTPResponseException as e:
        last_error = json.dumps({
            "message": str(e),
            "smtp_code": e.smtp_code,
            })
        scheduler.last_error = last_error
        scheduler.success = False
        scheduler.save()
        return str(e)
    except Exception as e:
        last_error = json.dumps({
            "message": str(e),
            })
        scheduler.last_error = last_error
        scheduler.success = False
        scheduler.save()
        return str(e)
    scheduler.last_error = None
    scheduler.success = True
    scheduler.save()
    return None


def revoke_student_permissions(scheduler: Scheduler):
    """
    revoke article permissions from students when scheduled
    """
    try:
        u = User.objects.filter(pk=int(scheduler.data)).first()

        add_perm = Permission.objects.filter(codename='add_article').first()
        change_perm = Permission.objects.filter(codename='change_article').first()
        delete_perm = Permission.objects.filter(codename='delete_article').first()
        view_perm = Permission.objects.filter(codename='view_article').first()

        u.user_permissions.remove(add_perm, change_perm, delete_perm, view_perm)

        scheduler.success = True
        scheduler.save()
        return None
    except Exception as e:
        return str(e)


def send_irc_msgs(schedulers):
    """
    sends the irc messages from `send_irc_msg` `Scheduler` objects
    and returns any error encountered
    """
    try:
        send_message([_.data for _ in schedulers])
        for s in schedulers:
            s.success = True
            s.save()
        return None
    except Exception as e:
        return str(e)


def send_reg_reminder(scheduler: Scheduler):
    try:
        data = json.loads(scheduler.data)
        reglink = RegLink.objects.get(pk=data['object_pk'])
        if reglink.is_usable():
            return send_email(scheduler)
        else:
            return "link already used"
    except Exception as e:
        return str(e)


def add_blog_counter(scheduler: Scheduler):
    try:
        gsoc_year = GsocYear.objects.first()
        current_profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
        for profile in current_profiles:
            profile.current_blog_count += 1
            profile.save()
        return None
    except Exception as e:
        return str(e)


def add_calendar_event(scheduler: Scheduler):
    try:
        pk = json.loads(scheduler.data)['event']
        event = Event.objects.get(pk=pk)
        event.add_to_calendar()
        return None
    except Exception as e:
        return str(e)


def update_site_template(scheduler: Scheduler):
    try:
        template = json.loads(scheduler.data)['template']
        gsoc_year = GsocYear.objects.first()
        if template == 'deadlines.html':
            context = {
                'events': Event.objects.filter(timeline__gsoc_year=gsoc_year).all(),
                'duedates': BlogPostDueDate.objects.filter(timeline__gsoc_year=gsoc_year).all(),
                }
        elif template == 'index.html':
            # change this if the number of contact fields increase
            contact_fields = ('chat', 'mailing_list', 'twitter_url', 'blog_url', 'link')
            suborgs = SubOrgDetails.objects.filter(gsoc_year=gsoc_year, accepted=True).all()
            suborg_list = []
            for suborg in suborgs:
                _ = {
                    'name': suborg.suborg.suborg_name,
                    'description': suborg.description,
                    'logo': f'/{suborg.logo.name}',
                    'ideas_list': suborg.ideas_list,
                    'contact': []
                    }
                contact_count = 0
                for field in contact_fields:
                    if getattr(suborg, field):
                        contact_count += 1
                        _['contact'].append((field.title().replace('_', ' '),
                                             getattr(suborg, field)))
                _['count'] = (contact_count // 2) + 1
                suborg_list.append(_)
            context = {
                'suborgs': suborg_list
                }
        content = render_site_template(template, context)
        push_site_template(settings.GITHUB_FILE_PATH[template], content)
    except Exception as e:
        return str(e)


def archive_gsoc_pages(scheduler: Scheduler):
    try:
        gsoc_year = GsocYear.objects.first()
        archive_current_gsoc_files(gsoc_year.gsoc_year)
    except Exception as e:
        return str(e)
