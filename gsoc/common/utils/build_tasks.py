from datetime import datetime, timedelta
import json
import uuid
from django.conf import settings

from django.utils import timezone
from gsoc.settings import ADMINS

from gsoc.models import (
    Event,
    GsocEndDate,
    GsocEndDateDefault,
    GsocStartDate, Timeline,
    UserProfile,
    GsocYear,
    BlogPostDueDate,
    Scheduler,
    ReaddUser
)
from gsoc.common.utils.tools import build_send_mail_json

from googleapiclient.discovery import build
from gsoc.models import getCreds


def build_pre_blog_reminders(builder):
    try:
        data = json.loads(builder.data)
        due_date = BlogPostDueDate.objects.get(pk=data["due_date_pk"])
        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(
            gsoc_year=gsoc_year,
            role=3,
            gsoc_end__gte=due_date.date
        ).all()
        categories = ((0, "Weekly Check-In"), (1, "Blog Post"))
        category = categories[due_date.category][1]
        for profile in profiles:
            if profile.current_blog_count != 0 and not (
                profile.hidden or profile.reminder_disabled
            ):
                template_data = {
                    "current_blog_count": profile.current_blog_count,
                    "type": due_date.category,
                    "due_date": due_date.date.strftime("%d %B %Y"),
                }

                scheduler_data = build_send_mail_json(
                    profile.user.email,
                    template="pre_blog_reminder.html",
                    subject=f"Reminder for {category}",
                    template_data=template_data,
                )

                s = Scheduler.objects.create(command="send_email", data=scheduler_data)
        return None
    except Exception as e:
        return str(e)


def build_post_blog_reminders(builder):
    try:
        data = json.loads(builder.data)
        last_due_date = BlogPostDueDate.objects.last()
        due_date = BlogPostDueDate.objects.get(pk=data["due_date_pk"])
        if due_date == last_due_date:
            blogs_count = 0
        else:
            blogs_count = 1

        categories = ((0, "Weekly Check-In"), (1, "Blog Post"))
        category = categories[due_date.category][1]

        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(
            gsoc_year=gsoc_year,
            role=3,
            gsoc_end__gte=due_date.date
            ).all()
        for profile in profiles:
            if profile.current_blog_count > blogs_count and not (
                profile.hidden or profile.reminder_disabled
            ):
                suborg = profile.suborg_full_name
                mentors = UserProfile.objects.filter(suborg_full_name=suborg, role=2)
                suborg_admins = UserProfile.objects.filter(
                    suborg_full_name=suborg, role=1
                )

                activation_date = builder.activation_date.date()

                if activation_date - due_date.date == timezone.timedelta(days=1):
                    student_template = "first_post_blog_reminder_student.html"

                elif activation_date - due_date.date == timezone.timedelta(days=3):
                    student_template = "second_post_blog_reminder_student.html"

                    mentors_emails = ["gsoc-admins@python.org"]
                    mentors_emails.extend([_.user.email for _ in mentors])
                    mentors_emails.extend([_.user.email for _ in suborg_admins])

                    mentors_template_data = {
                        "student_username": profile.user.username,
                        "student_email": profile.user.email,
                        "suborg_name": profile.suborg_full_name.suborg_name,
                        "due_date": due_date.date.strftime("%d %B %Y"),
                        "current_blog_count": profile.current_blog_count,
                    }

                    scheduler_data_mentors = build_send_mail_json(
                        mentors_emails,
                        template="post_blog_reminder_mentors.html",
                        subject=f"{category} missed by a Student of your Sub-Org",
                        template_data=mentors_template_data,
                    )

                    Scheduler.objects.create(
                        command="send_email", data=scheduler_data_mentors
                    )

                student_template_data = {
                    "current_blog_count": profile.current_blog_count,
                    "due_date": due_date.date.strftime("%d %B %Y"),
                }

                scheduler_data_student = build_send_mail_json(
                    profile.user.email,
                    template=student_template,
                    subject=f"Reminder for {category}",
                    template_data=student_template_data,
                )

                Scheduler.objects.create(
                    command="send_email", data=scheduler_data_student
                )
        return None
    except Exception as e:
        return str(e)


def build_revoke_student_perms(builder):
    try:
        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(gsoc_year=gsoc_year, role=3).all()
        for profile in profiles:
            Scheduler.objects.create(
                command="revoke_student_permissions", data=profile.user.id
            )
    except Exception as e:
        return str(e)


def build_remove_user_details(builder):
    try:
        gsoc_year = GsocYear.objects.first()
        profiles = UserProfile.objects.filter(
            gsoc_year=gsoc_year, role__in=[1, 2, 3]
        ).all()
        for profile in profiles:
            email = profile.user.email
            profile.user.email = None
            profile.user.save()
            _uuid = uuid.uuid4()
            ReaddUser.objects.create(user=profile.user, uuid=_uuid)
            template_data = {
                # TODO: change this after the view is created
                "link": settings.INETLOCATION
                + "use reverse here"
            }
            scheduler_data = build_send_mail_json(
                email,
                template="readd_email.html",
                subject="Your personal details have been removed from our database",
                template_data=template_data,
            )
            Scheduler.objects.create(command="send_email", data=scheduler_data)
    except Exception as e:
        return str(e)


def build_add_timeline_to_calendar(builder):
    data = json.loads(builder.data)
    if not data["calendar_id"]:
        creds = getCreds()
        if creds:
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            calendar = {"summary": "GSoC @ PSF Calendar", "timezone": "UTC"}
            calendar = service.calendars().insert(body=calendar).execute()
            timeline = Timeline.objects.get(id=data["timeline_id"])
            timeline.calendar_id = calendar.get("id")
            timeline.save()
        else:
            raise Exception(
                f"Please get the Access Token: " +
                f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
            )


def build_add_bpdd_to_calendar(builder):
    data = json.loads(builder.data)
    creds = getCreds()
    if creds:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": data["title"],
            "start": {"date": data["date"]},
            "end": {"date": data["date"]},
        }
        cal_id = builder.timeline.calendar_id if builder.timeline else "primary"
        if not data["event_id"]:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            item = BlogPostDueDate.objects.get(id=data["id"])
            item.event_id = event.get("id")
            item.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=data["event_id"], body=event
            ).execute()
    else:
        raise Exception(
            f"Please get the Access Token: " +
            f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
        )


def build_add_event_to_calendar(builder):
    data = json.loads(builder.data)
    creds = getCreds()
    if creds:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": data["title"],
            "start": {"date": data["start_date"]},
            "end": {"date": data["end_date"]},
        }
        cal_id = builder.timeline.calendar_id if builder.timeline else "primary"
        item = Event.objects.get(id=data["id"])
        if not data["event_id"]:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            item.event_id = event.get("id")
            item.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=item.event_id, body=event
            ).execute()
    else:
        raise Exception(
            f"Please get the Access Token: " +
            f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
        )


def build_add_end_to_calendar(builder):
    data = json.loads(builder.data)
    creds = getCreds()
    if creds:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": data["title"],
            "start": {"date": data["date"]},
            "end": {"date": data["date"]},
        }
        cal_id = builder.timeline.calendar_id if builder.timeline else "primary"
        if not data["event_id"]:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            item = GsocEndDate.objects.get(id=data["id"])
            item.event_id = event.get("id")
            item.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=data["event_id"], body=event
            ).execute()
    else:
        raise Exception(
            f"Please get the Access Token: " +
            f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
        )


def build_add_start_to_calendar(builder):
    data = json.loads(builder.data)
    creds = getCreds()
    if creds:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": data["title"],
            "start": {"date": data["date"]},
            "end": {"date": data["date"]},
        }
        cal_id = builder.timeline.calendar_id if builder.timeline else "primary"
        if not data["event_id"]:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            item = GsocStartDate.objects.get(id=data["id"])
            item.event_id = event.get("id")
            item.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=data["event_id"], body=event
            ).execute()
    else:
        raise Exception(
            f"Please get the Access Token: " +
            f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
        )


def build_add_end_standard_to_calendar(builder):
    data = json.loads(builder.data)
    creds = getCreds()
    if creds:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": data["title"],
            "start": {"date": data["date"]},
            "end": {"date": data["date"]},
        }
        cal_id = builder.timeline.calendar_id if builder.timeline else "primary"
        if not data["event_id"]:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            item = GsocEndDateDefault.objects.get(id=data["id"])
            item.event_id = event.get("id")
            item.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=data["event_id"], body=event
            ).execute()
    else:
        raise Exception(
            f"Please get the Access Token: " +
            f"{settings.OAUTH_REDIRECT_URI + 'authorize'}"
        )


def build_evaluation_reminder(builder):
    data = json.loads(builder.data)
    gsoc_year = GsocYear.objects.latest('gsoc_year')
    start_date = GsocStartDate.objects.latest('date')
    start_date = start_date.date
    exam_date = datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
    is_midterm = data["Midterm"]

    gsoc_end = exam_date
    if is_midterm:
        gsoc_end = start_date + 2 * (exam_date - start_date) + timedelta(days=7-1)

    # 4 days before
    notify_date = exam_date - timedelta(days=4)

    tl_users = UserProfile.objects.filter(
        gsoc_year=gsoc_year,
        role=3,
        gsoc_end=gsoc_end
    ).all()

    tl_suborg = [user.suborg_full_name for user in tl_users]

    profiles = UserProfile.objects.filter(
        suborg_full_name__in=tl_suborg,
        role__in=[1, 2]
    )

    for profile in profiles:
        template_data = {
            "date": str(exam_date),
        }

        scheduler_data = build_send_mail_json(
            profile.user.email,
            template="exam_reminder.html",
            subject=f"Evaluation Due Reminder",
            template_data=template_data,
        )

        Scheduler.objects.create(
            command="send_email",
            data=scheduler_data,
            activation_date=notify_date
        )

    # 2 days before
    notify_date = exam_date - timedelta(days=2)

    tl_users = UserProfile.objects.filter(
        gsoc_year=gsoc_year,
        role=3,
        gsoc_end=gsoc_end
    ).all()

    tl_suborg = [user.suborg_full_name for user in tl_users]

    profiles = UserProfile.objects.filter(
        suborg_full_name__in=tl_suborg,
        role__in=[1, 2]
    )

    for profile in profiles:
        template_data = {
            "date": str(exam_date),
        }

        scheduler_data = build_send_mail_json(
            profile.user.email,
            template="exam_reminder.html",
            subject=f"Evaluation Due Reminder",
            template_data=template_data,
        )

        Scheduler.objects.create(
            command="send_email",
            data=scheduler_data,
            activation_date=notify_date
        )

    template_data = {
        "date": str(exam_date),
    }

    scheduler_data = build_send_mail_json(
        ADMINS,
        template="exam_reminder.html",
        subject="Evaluation Due Reminder",
        template_data=template_data,
    )
    Scheduler.objects.create(
        command="send_email",
        data=scheduler_data,
        activation_date=notify_date
    )
