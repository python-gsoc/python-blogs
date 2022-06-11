import os
import re
import datetime
import uuid
import json
import bleach
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.db.models.deletion import PROTECT

from googleapiclient.discovery import build

from django.contrib.auth.models import Permission
from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.html import mark_safe
from django.core.validators import validate_email
from django.utils import timezone
from django.shortcuts import reverse
from django.conf import settings

from aldryn_apphooks_config.fields import AppHookConfigField

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.models import Article, Person

from cms.models import Page, PagePermission
from cms import api
from cms.utils.conf import get_cms_setting
from cms.utils.apphook_reload import mark_urlconf_as_changed

import phonenumbers
from phonenumbers.phonenumbermatcher import PhoneNumberMatcher

from gsoc.common.utils.tools import build_send_mail_json
from gsoc.common.utils.tools import build_send_reminder_json
from gsoc.settings import PROPOSALS_PATH

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Util Functions


def gen_uuid_str():
    return str(uuid.uuid4())


def getCreds():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


# Patching

NewsBlogConfig.__str__ = lambda self: self.app_title


def current_year_profile(self):
    gsoc_year = GsocYear.objects.first()
    profile = self.userprofile_set.filter(gsoc_year=gsoc_year, role__in=[1, 2, 3])
    return profile.first() if len(profile) > 0 else None


auth.models.User.add_to_class("current_year_profile", current_year_profile)


def has_proposal(self):
    try:
        proposal = self.student_profile().accepted_proposal_pdf
        return proposal is not None and proposal.path
    except BaseException:
        return False


auth.models.User.add_to_class("has_proposal", has_proposal)


def is_current_year_student(self):
    profile = self.student_profile()
    if not profile:
        return False
    year = profile.gsoc_year.gsoc_year
    current_year = timezone.now().year
    return current_year == year


auth.models.User.add_to_class("is_current_year_student", is_current_year_student)


def is_current_year_suborg_admin(self):
    profile = self.suborg_admin_profile()
    if not profile:
        return False
    year = profile.gsoc_year.gsoc_year
    current_year = timezone.now().year
    return current_year == year


auth.models.User.add_to_class(
    "is_current_year_suborg_admin", is_current_year_suborg_admin
)


def suborg_admin_profile(self, year=timezone.now().year):
    gsoc_year = GsocYear.objects.filter(gsoc_year=year).first()
    if gsoc_year is None:
        return None
    return self.userprofile_set.filter(role=1, gsoc_year=gsoc_year).first()


auth.models.User.add_to_class("suborg_admin_profile", suborg_admin_profile)


def student_profile(self, year=timezone.now().year):
    gsoc_year = GsocYear.objects.filter(gsoc_year=year).first()
    if gsoc_year is None:
        return None
    return self.userprofile_set.filter(role=3, gsoc_year=gsoc_year).first()


auth.models.User.add_to_class("student_profile", student_profile)


def get_root_comments(self):
    return self.comment_set.filter(parent=None).all()


Article.add_to_class("get_root_comments", get_root_comments)


def save(self, *args, **kwargs):
    tags = settings.BLEACH_ALLOWED_TAGS
    attrs = bleach.sanitizer.ALLOWED_ATTRIBUTES
    attrs.update(settings.BLEACH_ALLOWED_ATTRS)
    styles = settings.BLEACH_ALLOWED_STYLES
    self.lead_in = bleach.clean(
        self.lead_in, tags=tags, attributes=attrs, styles=styles
    )
    soup = BeautifulSoup(self.lead_in, "html5lib")
    for iframe_tag in soup.find_all("iframe"):
        _ = iframe_tag.attrs.get("src", None)
        if not (_ and "https://www.youtube.com/embed" in _):
            iframe_text = str(iframe_tag)
            self.lead_in = self.lead_in.replace(iframe_text, bleach.clean(iframe_text))

    # Update the search index
    if self.update_search_on_save:
        self.search_data = self.get_search_data()

    # Ensure there is an owner.
    if self.app_config.create_authors and self.author is None:
        self.author = Person.objects.get_or_create(
            user=self.owner,
            defaults={"name": " ".join((self.owner.first_name, self.owner.last_name))},
        )[0]
    # slug would be generated by TranslatedAutoSlugifyMixin
    self.lead_in = mark_safe(self.lead_in)
    super(Article, self).save(*args, **kwargs)


Article.save = save


# Models


class SubOrg(models.Model):
    class Meta:
        ordering = ["suborg_name"]

    suborg_name = models.CharField(name="suborg_name", max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    class Meta:
        ordering = ["-gsoc_year"]

    gsoc_year = models.IntegerField(name="gsoc_year",
                                    primary_key=True)

    def __str__(self):
        return str(self.gsoc_year)


class SubOrgDetails(models.Model):
    suborg_admin = models.ForeignKey(
        User,
        on_delete=PROTECT,
        related_name="suborg_admin",
        blank=True,
        null=True,
    )

    gsoc_year = models.ForeignKey(
        GsocYear,
        on_delete = models.CASCADE,
        related_name = "suborg_details",
        to_field = "gsoc_year",
    )

    suborg_admin_email = models.EmailField(verbose_name="Suborg admin email")

    suborg_admin_2_email = models.EmailField(
        verbose_name="Suborg admin 2 email",
        blank=True,
        null=True,
        help_text="Fill this if there are other suborg admins other than you",
    )

    suborg_admin_3_email = models.EmailField(
        verbose_name="Suborg admin 3 email",
        blank=True,
        null=True,
        help_text="Fill this if there are other suborg admins other than you",
    )

    past_gsoc_experience = models.BooleanField(
        verbose_name="Has your org been accepted as a mentor org "
        "in Google Summer of Code before?",
        help_text="Mark the checkbox for yes",
    )
    suborg_in_past = models.BooleanField(
        verbose_name="Was this as a Suborg?", help_text="Mark the checkbox for yes"
    )

    source_code = models.URLField(verbose_name="Where does your source code live?")
    docs = models.URLField(
        verbose_name="Please provide the URL that points to the repository, "
        "GitHub organization, or a web page that describes how to"
        " get your source code"
    )
    anything_else = models.TextField(
        null=True, blank=True, verbose_name="Anything else we should know (optional)"
    )

    suborg = models.ForeignKey(
        SubOrg,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Select your suborg, if " "you have applied before",
    )
    suborg_name = models.CharField(
        max_length=80,
        verbose_name="If applying for the first time" " enter the name of your suborg",
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name="A very short description of your organization"
    )
    logo = models.ImageField(
        upload_to="logos/",
        verbose_name="Your organization logo",
        help_text="Must be a 24-bit PNG of 256 x 256 pixels.",
    )
    primary_os_license = models.CharField(
        max_length=50, verbose_name="Primary Open Source License"
    )
    ideas_list = models.URLField(verbose_name="Ideas List")

    chat = models.CharField(max_length=80, null=True, blank=True)
    mailing_list = models.CharField(max_length=80, null=True, blank=True)
    twitter_url = models.URLField(null=True, blank=True)
    blog_url = models.URLField(null=True, blank=True)
    homepage = models.URLField(null=True, blank=True, verbose_name="Homepage")

    last_message = models.TextField(null=True, blank=True)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    last_reviewed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    accepted = models.BooleanField(default=False)
    changed = models.BooleanField(default=None, null=True)

    class Meta:
        verbose_name_plural = "Suborg Details"

    def accept(self, suborg):
        self.accepted = True
        self.suborg = suborg
        self.save()

        template_data = {
            "gsoc_year": self.gsoc_year.gsoc_year,
            "suborg_name": self.suborg.suborg_name,
        }
        suborg_email_list = [', '.join(str(x) for x in settings.ADMINS),str(self.suborg_admin_email)]
        try:
            if self.suborg_admin_2_email is not None:
                suborg_email_list.append(self.suborg_admin_2_email)
        except NameError:
            pass
        try:
            if self.suborg_admin_3_email is not None:
                suborg_email_list.append(self.suborg_admin_3_email)
        except NameError:
            pass
        scheduler_data = build_send_mail_json(
            suborg_email_list,
            template="suborg_accept.html",
            subject="Acceptance for GSoC@PSF {}".format(self.gsoc_year.gsoc_year),
            template_data=template_data,
        )
        Scheduler.objects.create(command="send_email", data=scheduler_data)

        s = Scheduler.objects.filter(
            command="update_site_template",
            data=json.dumps({"template": "ideas.html"}),
            success=None,
        ).all()
        if len(s) == 0:
            time = timezone.now() + timezone.timedelta(minutes=5)
            Scheduler.objects.create(
                command="update_site_template",
                data=json.dumps({"template": "ideas.html"}),
                activation_date=time,
            )

    def send_update_notification(self):
        if self.suborg:
            suborg_name = self.suborg.suborg_name
        else:
            suborg_name = self.suborg_name

        template_data = {"suborg_name": suborg_name}
        scheduler_data = build_send_mail_json(
            settings.ADMINS,
            template="suborg_application_notification.html",
            subject="Review new/updated SubOrg Application",
            template_data=template_data,
        )
        Scheduler.objects.create(command="send_email", data=scheduler_data)

    def send_review(self):
        self.accepted = False
        self.save()

        if self.suborg:
            suborg_name = self.suborg.suborg_name
        else:
            suborg_name = self.suborg_name

        template_data = {
            "gsoc_year": self.gsoc_year.gsoc_year,
            "suborg_name": suborg_name,
            "message": self.last_message,
        }
        suborg_email_list = [', '.join(str(x) for x in settings.ADMINS),str(self.suborg_admin_email)]
        try:
            if self.suborg_admin_2_email is not None:
                suborg_email_list.append(self.suborg_admin_2_email)
        except NameError:
            pass
        try:
            if self.suborg_admin_3_email is not None:
                suborg_email_list.append(self.suborg_admin_3_email)
        except NameError:
            pass
        scheduler_data = build_send_mail_json(
            suborg_email_list,
            template="suborg_review.html",
            subject="Review your SubOrg Application"
            " for GSoC@PSF {}".format(self.gsoc_year.gsoc_year),
            template_data=template_data,
        )
        Scheduler.objects.create(command="send_email", data=scheduler_data)


class ReaddUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100)

    def readd_user_details(self, email):
        self.user.email = email
        self.user.save()


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)

class UserProfile(models.Model):
    ROLES = ((0, "Others"), (1, "Suborg Admin"), (2, "Mentor"), (3, "Student"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(name="role", choices=ROLES, default=0)
    gsoc_year = models.ForeignKey(
        GsocYear,
        on_delete = models.CASCADE,
        null = True,
        blank = False,
        to_field = "gsoc_year"
    )
    suborg_full_name = models.ForeignKey(
        SubOrg, on_delete=models.CASCADE, null=True, blank=False
    )
    accepted_proposal_pdf = models.FileField(
        blank=True, null=True, upload_to=PROPOSALS_PATH
    )
    proposal_confirmed = models.BooleanField(default=False)
    app_config = AppHookConfigField(
        NewsBlogConfig, verbose_name=_("Section"), blank=True, null=True
    )
    hidden = models.BooleanField(name="hidden", default=False)
    reminder_disabled = models.BooleanField(default=False)
    current_blog_count = models.IntegerField(default=0)
    github_handle = models.TextField(null=True, blank=True, max_length=100)
    gsoc_invited = models.BooleanField(default=False)

    objects = UserProfileManager()
    all_objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['suborg_full_name', 'user',
                                            'gsoc_year'],
                                    name='unique_draft_user')
        ]

    def confirm_proposal(self):
        self.proposal_confirmed = True
        self.save()

    def save(self, *args, **kwargs):
        if self.user is None:
            raise Exception("User must not be empty!")
        if self.role == 0 or self.role is None:
            raise Exception("User must have a role!")
        if self.gsoc_year != GsocYear.objects.get(gsoc_year=datetime.datetime.now().year):
            raise Exception("Not current year!")
        if self.suborg_full_name is None:
            raise Exception("Suborg must not be empty!")

        # duplicate check
        try:
            user = UserProfile.objects.get(user=self.user)
            if all([
                self.role == user.role,
                self.suborg_full_name == user.suborg_full_name,
                self.gsoc_year == user.gsoc_year
            ]):
                raise Exception("UserProfile already exists!!")
        except Exception:
            pass

        super(UserProfile, self).save(*args, **kwargs)


class SuborgProfile(UserProfile):
    class Meta:
        proxy = True


class AdminGSOCInvites(UserProfile):

    class Meta:
        proxy = True

class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    deactivation_date = models.DateTimeField(
        name="deactivation_date", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "User details"

    def save(self, *args, **kwargs):
        if self.deactivation_date:
            s = Scheduler(
                command="deactivate_user",
                data=self.user.pk,
                activation_date=self.deactivation_date,
            )
            s.save()

        super(UserDetails, self).save(*args, **kwargs)


class Scheduler(models.Model):
    commands = (
        ("send_email", "send_email"),
        ("send_irc_msg", "send_irc_msg"),
        ("revoke_student_permissions", "revoke_student_permissions"),
        ("send_reg_reminder", "send_reg_reminder"),
        ("add_blog_counter", "add_blog_counter"),
        ("update_site_template", "update_site_template"),
        ("archive_gsoc_pages", "archive_gsoc_pages"),
    )

    id = models.AutoField(primary_key=True)
    command = models.CharField(name="command", max_length=40, choices=commands)
    activation_date = models.DateTimeField(
        name="activation_date", null=True, blank=True
    )
    data = models.TextField(name="data")
    success = models.BooleanField(name="success", null=True)
    last_error = models.TextField(
        name="last_error", null=True, default=None, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.command


class Builder(models.Model):
    categories = (
        ("build_pre_blog_reminders", "build_pre_blog_reminders"),
        ("build_post_blog_reminders", "build_post_blog_reminders"),
        ("build_revoke_student_perms", "build_revoke_student_perms"),
        ("build_remove_user_details", "build_remove_user_details"),
    )

    category = models.CharField(max_length=40, choices=categories)
    activation_date = models.DateTimeField(null=True, blank=True)
    built = models.BooleanField(default=None, null=True)
    data = models.TextField()
    last_error = models.TextField(null=True, default=None, blank=True)

    def __str__(self):
        return self.category


class Timeline(models.Model):
    gsoc_year = models.ForeignKey(
        GsocYear,
        on_delete = models.CASCADE,
        to_field = "gsoc_year")
    calendar_id = models.CharField(max_length=255, null=True, blank=True)

    def add_calendar(self):
        if not self.calendar_id:
            creds = getCreds()
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            calendar = {"summary": "GSoC @ PSF Calendar", "timezone": "UTC"}
            calendar = service.calendars().insert(body=calendar).execute()
            self.calendar_id = calendar.get("id")
            self.save()


class Event(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    timeline = models.ForeignKey(
        Timeline, on_delete=models.CASCADE, null=True, blank=True
    )
    event_id = models.CharField(max_length=255, null=True, blank=True)

    @property
    def calendar_link(self):
        if self.event_id:
            creds = getCreds()
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            event = (
                service.events()
                .get(calendarId=self.timeline.calendar_id, eventId=self.event_id)
                .execute()
            )
            return event.get("htmlLink", None)
        return None

    def add_to_calendar(self):
        creds = getCreds()
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": self.title,
            "start": {"date": self.start_date.strftime("%Y-%m-%d")},
            "end": {"date": self.end_date.strftime("%Y-%m-%d")},
        }
        cal_id = self.timeline.calendar_id if self.timeline else "primary"
        if not self.event_id:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            self.event_id = event.get("id")
            self.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=self.event_id, body=event
            ).execute()

    def delete_from_calendar(self):
        if self.event_id:
            creds = getCreds()
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            service.events().delete(
                calendarId=self.timeline.calendar_id, eventId=self.event_id
            ).execute()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date
        super().save(*args, **kwargs)


class BlogPostHistory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)


class BlogPostDueDate(models.Model):
    categories = ((0, "Weekly Check-In"), (1, "Blog Post"))

    class Meta:
        ordering = ["date"]

    title = models.CharField(max_length=100, default="Weekly Blog Post Due")
    date = models.DateField()
    timeline = models.ForeignKey(
        Timeline,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    add_counter_scheduler = models.ForeignKey(
        Scheduler,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    pre_blog_reminder_builder = models.ForeignKey(
        Builder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pre"
    )
    post_blog_reminder_builder = models.ManyToManyField(Builder, blank=True)
    event_id = models.CharField(max_length=255, null=True, blank=True)
    category = models.IntegerField(choices=categories, null=True, blank=True)

    def add_to_calendar(self):
        creds = getCreds()
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": self.title,
            "start": {"date": self.date.strftime("%Y-%m-%d")},
            "end": {"date": self.date.strftime("%Y-%m-%d")},
        }
        cal_id = self.timeline.calendar_id if self.timeline else "primary"
        if not self.event_id:
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event)
                .execute()
            )
            self.event_id = event.get("id")
            self.save()
        else:
            service.events().update(
                calendarId=cal_id, eventId=self.event_id, body=event
            ).execute()

    def delete_from_calendar(self):
        if self.event_id:
            creds = getCreds()
            service = build("calendar", "v3", credentials=creds, cache_discovery=False)
            service.events().delete(
                calendarId=self.timeline.calendar_id, eventId=self.event_id
            ).execute()

    def create_scheduler(self):
        s = Scheduler.objects.create(
            command="add_blog_counter",
            activation_date=self.date + datetime.timedelta(days=-6),
            data="{}",
        )
        self.add_counter_scheduler = s
        self.save()

    def create_builders(self):
        builder_data = json.dumps({"due_date_pk": self.pk})

        s = Builder.objects.create(
            category="build_pre_blog_reminders",
            activation_date=self.date + datetime.timedelta(days=-3),
            data=builder_data,
        )
        self.pre_blog_reminder_builder = s

        s = Builder.objects.create(
            category="build_post_blog_reminders",
            activation_date=self.date + datetime.timedelta(days=1),
            data=builder_data,
        )
        self.post_blog_reminder_builder.add(s)

        s = Builder.objects.create(
            category="build_post_blog_reminders",
            activation_date=self.date + datetime.timedelta(days=3),
            data=builder_data,
        )
        self.post_blog_reminder_builder.add(s)

        self.save()


class GsocEndDate(models.Model):
    timeline = models.OneToOneField(Timeline, on_delete=models.CASCADE)
    date = models.DateField()


class PageNotification(models.Model):
    message = models.TextField(name="message")
    user = models.ForeignKey(User, name="user", on_delete=models.CASCADE)
    page = models.ForeignKey(
        Page,
        name="page",
        related_name="notifications",
        on_delete=models.CASCADE
    )
    pubished_page = models.ForeignKey(
        Page,
        name="published_page",
        related_name="notifications_for_published",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if self.page and self.page.publisher_is_draft:
            page = self.page
            published_page = Page.objects.filter(
                node_id=page.node_id, publisher_is_draft=False
            ).first()
            self.published_page = published_page
            perm = (
                PagePermission.objects.filter(page=page).filter(user=self.user).first()
            )

            if self.user.is_superuser or (perm and perm.can_change):
                super().save(*args, **kwargs)
            else:
                raise ValidationError(
                    message="User does not have permissions on this page"
                )
        else:
            raise ValidationError(message="Add notification on unpublished page")


class ProposalTextValidator:
    def find_all_emails(self, text):
        """
        Returns all emails in the text in a list.
        """
        quick_email_pattern = re.compile(
            """
        [a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@
        (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
        """,
            re.X,
        )
        emails = re.findall(quick_email_pattern, text)
        real_emails = []
        for email in emails:
            try:
                validate_email(email)
                real_emails.append(email)
            except BaseException:
                pass
        return real_emails

    def find_all_possible_phone_numbers(self, text):
        """
        Returns all possible phone numbers in a list.
        """
        matcher = PhoneNumberMatcher(text, "US")
        all_numbers = list(iter(matcher))
        all_number_strings = [x.raw_string for x in all_numbers]
        ptn = re.compile(r"\+?[0-9][0-9\(\)\-\ ]{3,}[0-9]", re.A | re.M)
        maybe_numbers = re.findall(ptn, text)
        for maybe_number in maybe_numbers:
            if maybe_number in all_number_strings:
                continue
            try:
                maybe_number_parsed = phonenumbers.parse(maybe_number)
                if phonenumbers.is_possible_number(maybe_number_parsed):
                    all_number_strings.append(maybe_number)
            except BaseException:
                pass
        return all_number_strings

    def find_all_locations(self, text):
        return []

    def validate(self, text):
        emails = self.find_all_emails(text)
        possible_phone_numbers = self.find_all_possible_phone_numbers(text)
        locations = self.find_all_locations(text)
        if any((emails, possible_phone_numbers, locations)):
            message = {
                "emails": emails,
                "possible_phone_numbers": possible_phone_numbers,
                "locations": locations,
            }
            raise ValidationError(message=message)

    def __call__(self, text):
        self.validate(text)

    def get_help_text(self):
        return _("The text in a proposal should not contain any private data.")


class AddUserLog(models.Model):
    class Meta:
        verbose_name = "Add Users " "(The invites will be sent to the emails on save)"
        verbose_name_plural = (
            "Add Users " "(The invites will be sent to the emails on save)"
        )

    log_id = models.CharField(max_length=36, default=gen_uuid_str)

    def __str__(self):
        return self.log_id


class RegLink(models.Model):
    is_used = models.BooleanField(default=False, editable=False)
    reglink_id = models.CharField(
        max_length=36,
        default=gen_uuid_str,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user_role = models.IntegerField(
        name="user_role",
        choices=UserProfile.ROLES,
        default=0,
        null=True,
        blank=False
    )
    user_suborg = models.ForeignKey(
        SubOrg,
        name="user_suborg",
        on_delete=models.CASCADE,
        null=True,
        blank=False
    )
    gsoc_year = models.ForeignKey(
        GsocYear,
        name = "gsoc_year",
        on_delete = models.CASCADE,
        null = True,
        blank = False,
        to_field = "gsoc_year",
    )
    adduserlog = models.ForeignKey(
        AddUserLog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reglinks",
    )
    email = models.CharField(
        null=False,
        blank=False,
        default="",
        max_length=300,
        validators=[validate_email]
    )
    scheduler = models.ForeignKey(
        Scheduler,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        editable=False
    )
    reminder = models.ForeignKey(
        Scheduler,
        null=True,
        related_name="reglinks",
        blank=True,
        on_delete=models.CASCADE,
        editable=False,
    )
    send_notifications = models.BooleanField(default=True)

    @property
    def has_scheduler(self):
        return self.scheduler is not None

    @property
    def has_reminder(self):
        return self.reminder is not None

    @property
    def url(self):
        return f'{reverse("register")}?reglink_id={self.reglink_id}'

    @property
    def is_sent(self):
        return self.scheduler is not None and self.scheduler.success

    def __str__(self):
        sent = self.is_sent
        if sent:
            sent_str = "Sent."
        else:
            sent_str = "Not sent."
        return f"Register Link {self.url} for {self.email}. {sent_str}"

    def is_usable(self):
        timenow = timezone.now()
        return (not self.is_used) and self.created_at < timenow

    def create_user(
        self,
        *args,
        is_staff=True,
        reminder_disabled=False,
        github_handle=None,
        **kwargs,
    ):
        namespace = str(uuid.uuid4())
        email = kwargs.get("email", self.email)
        user, created = User.objects.get_or_create(
            *args, is_staff=is_staff, email=email, **kwargs
        )
        if not created and not github_handle:
            profiles = user.userprofile_set.all()
            for profile in profiles:
                if profile.github_handle:
                    github_handle = profile.github_handle
                    break

        role = {k: v for v, k in UserProfile.ROLES}

        try:
            profile = UserProfile.objects.create(
                user=user,
                role=self.user_role,
                gsoc_year=self.gsoc_year,
                suborg_full_name=self.user_suborg,
                reminder_disabled=reminder_disabled,
                github_handle=github_handle,
            )
        except Exception:
            profile = None

        if self.user_role != role.get("Student", 3):
            try:
                profile.save()
            except Exception:
                pass
            return user

        # setup blog
        blogname = f"{user.username}'s Blog"
        app_config = NewsBlogConfig.objects.create(namespace=namespace)
        app_config.app_title = blogname
        app_config.save()
        profile.app_config = app_config
        profile.save()
        blog_list_page = (
            Page.objects.filter(application_namespace="blogs_list")
            .filter(publisher_is_draft=True)
            .first()
        )
        page = api.create_page(
            blogname,
            get_cms_setting("TEMPLATES")[0][0],
            "en",
            published=True,
            publication_date=timezone.now(),
            apphook=app_config.cmsapp,
            apphook_namespace=namespace,
            parent=blog_list_page,
        )
        su = User.objects.filter(is_superuser=True).first()
        page = api.publish_page(page, su, "en")

        PagePermission.objects.create(user=user, page=page)

        perms = list()
        pobjs = Permission.objects
        perms.append(pobjs.filter(codename="add_article").first())
        perms.append(pobjs.filter(codename="change_article").first())
        perms.append(pobjs.filter(codename="delete_article").first())
        perms.append(pobjs.filter(codename="view_article").first())
        perms.append(pobjs.filter(codename="add_pagenotification").first())
        perms.append(pobjs.filter(codename="change_pagenotification").first())
        perms.append(pobjs.filter(codename="delete_pagenotification").first())
        perms.append(pobjs.filter(codename="view_pagenotification").first())
        user.user_permissions.set(perms)

        mark_urlconf_as_changed()
        return user

    def create_scheduler(self, trigger_time=timezone.now()):
        validate_email(self.email)
        role = {0: "Others", 1: "Suborg Admin", 2: "Mentor", 3: "Student"}
        template_data = {
            "register_link": settings.INETLOCATION + self.url,
            "role": self.user_role,
            "gsoc_year": self.gsoc_year.gsoc_year,
        }
        if self.user_role == 0:
            subject = (
                f"You have been invited to join for GSoC "
                f"{self.gsoc_year.gsoc_year} with PSF"
            )
        else:
            subject = (
                f"You have been invited to join "
                f"{self.user_suborg.suborg_name.strip()}"
                f" as a {role[self.user_role]} for GSoC "
                f"{self.gsoc_year.gsoc_year} with PSF"
            )
            template_data["suborg"] = self.user_suborg.suborg_name.strip()
        scheduler_data = build_send_mail_json(
            self.email,
            template="invite.html",
            subject=subject,
            template_data=template_data,
        )
        s = Scheduler.objects.create(
            command="send_email",
            activation_date=trigger_time,
            data=scheduler_data
        )
        self.scheduler = s
        self.save()

    def create_reminder(self, trigger_time=None):
        if self.has_scheduler:
            validate_email(self.email)
            register_link = settings.INETLOCATION + self.url
            scheduler_data = build_send_reminder_json(
                self.email,
                self.pk,
                template="registration_reminder.html",
                subject="Reminder for registration",
                template_data={"register_link": register_link},
            )

            if not trigger_time:
                activation_date = self.scheduler.activation_date + datetime.timedelta(
                    days=3
                )
            else:
                activation_date = trigger_time

            s = Scheduler.objects.create(
                command="send_reg_reminder",
                activation_date=activation_date,
                data=scheduler_data,
            )
            self.reminder = s
            self.save()
        else:
            self.create_scheduler()

    def save(self, *args, **kwargs):
        try:
            reglink = RegLink.objects.get(
                user_role=self.user_role,
                gsoc_year=self.gsoc_year,
                email=self.email,
                user_suborg=self.user_suborg
            ).delete()
            if reglink.scheduler_id is not None and reglink.reminder_id is not None:
                Scheduler.objects.get(id=reglink.scheduler_id).delete()
                Scheduler.objects.get(id=reglink.reminder_id).delete()

        except Exception:
            pass
        super(RegLink, self).save(*args, **kwargs)


class Comment(models.Model):
    username = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.CharField(max_length=1100)
    parent = models.ForeignKey(
        "self", null=True, on_delete=models.CASCADE, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def send_notifications(self):
        article_link = self.article.get_absolute_url()
        comment_link = "{}#comment-{}".format(article_link, self.pk)
        template_data = {
            "article": self.article.title,
            "created_at": self.created_at.strftime("%I:%M %p, %d %B %Y"),
            # "username": self.username,
            "link": urljoin(settings.INETLOCATION, comment_link),
            "article_owner": self.article.owner.username,
        }
        scheduler_data = build_send_mail_json(
            self.article.owner.email,
            template="comment_notification.html",
            subject="{} commented on your article".format(self.username),
            template_data=template_data,
        )
        Scheduler.objects.create(command="send_email", data=scheduler_data)

        if self.parent and self.parent.user:
            template_data["parent_comment_owner"] = self.parent.username
            scheduler_data = build_send_mail_json(
                self.parent.user.email,
                template="comment_reply_notification.html",
                subject="{} replied to your comment".format(self.username),
                template_data=template_data,
            )
            Scheduler.objects.create(command="send_email", data=scheduler_data)


class ArticleReview(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    last_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"is_superuser": True},
    )
    is_reviewed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.last_reviewed_by:
            if not self.last_reviewed_by.is_superuser:
                raise ValidationError(
                    "The user does not have permissions to review an article."
                )
        super(ArticleReview, self).save(*args, **kwargs)


class SendEmail(models.Model):
    groups = (
        ("students", "Students"),
        ("mentors", "Mentors"),
        ("suborg_admins", "Suborg Admins"),
        ("admins", "Admins"),
        ("all", "All"),
    )

    to = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        help_text="Separate email with a comma"
    )
    to_group = models.CharField(
        max_length=80,
        choices=groups,
        null=True,
        blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    activation_date = models.DateTimeField(blank=True, null=True)
    scheduler = models.ForeignKey(
        Scheduler, blank=True, null=True, on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not (self.to or self.to_group):
            raise ValidationError(
                message="Any one of the fields 'to' or 'to_group' should be filled."
            )
        emails = []
        if self.to:
            emails.extend(self.to.split(","))

        gsoc_year = GsocYear.objects.first()

        if self.to_group == "students":
            ups = UserProfile.objects.filter(role=3, gsoc_year=gsoc_year).all()
            emails.extend([_.user.email for _ in ups])
        elif self.to_group == "mentors":
            ups = UserProfile.objects.filter(role=2, gsoc_year=gsoc_year).all()
            emails.extend([_.user.email for _ in ups])
        elif self.to_group == "suborg_admins":
            ups = UserProfile.objects.filter(role=1, gsoc_year=gsoc_year).all()
            emails.extend([_.user.email for _ in ups])
        elif self.to_group == "admins":
            ups = User.objects.filter(is_superuser=True)
            emails.extend([_.user.email for _ in ups])
        elif self.to_group == "all":
            ups = UserProfile.objects.filter(gsoc_year=gsoc_year).all()
            emails.extend([_.user.email for _ in ups])

        scheduler_data = build_send_mail_json(
            emails,
            template="generic_email.html",
            subject=self.subject,
            template_data={"body": self.body},
        )
        self.scheduler = Scheduler.objects.create(
            command="send_email",
            data=scheduler_data,
            activation_date=self.activation_date,
        )

        super(SendEmail, self).save(*args, **kwargs)


class NotAcceptedUser(RegLink):
    class Meta:
        proxy = True


# Receivers

# Update blog count when new UserProfile is created
@receiver(models.signals.pre_save, sender=UserProfile)
def update_blog_counter(sender, instance, **kwargs):
    if not instance.pk:
        # increase blog counter
        date = timezone.now() + datetime.timedelta(days=6)
        currentYear = datetime.datetime.now().year
        due_dates = BlogPostDueDate.objects.filter(date__year=currentYear, date__lt=date).all()
        instance.current_blog_count = len(due_dates)


# Delete blog when student profile is deleted
@receiver(models.signals.post_delete, sender=UserProfile)
def delete_blog(sender, instance, **kwargs):
    """
    Deletes the blog of the deleted user if a student
    """
    if instance.app_config:
        instance.app_config.delete()


# Auto Delete Redundant Proposal
@receiver(models.signals.post_delete, sender=UserProfile)
def auto_delete_proposal_on_delete(sender, instance, **kwargs):
    """
    Deletes proposal after a UserProfile object is deleted.
    """
    if instance.accepted_proposal_pdf:
        try:
            filepath = instance.accepted_proposal_pdf.path
        except ValueError:
            return
        if os.path.isfile(filepath):
            os.remove(filepath)


# update user permission when user profile associated with the user is changed.
@receiver(models.signals.post_save, sender=UserProfile)
def update_user_permission(sender, instance, **kwargs):
    """
    If any user profile associated with user has role as suborg admin then add the
    view_suborgprofile permission to the user else remove the permission if present.
    """

    user = instance.user
    permission = Permission.objects.get(codename='view_suborgprofile')
    if user.userprofile_set.filter(role=1).count() > 0:
        user.user_permissions.add(permission)
    elif user.has_perm('gsoc.view_suborgprofile'):
        user.user_permissions.remove(permission)
    user.save()


# Auto Delete Proposal when new Proposal is uploaded
@receiver(models.signals.pre_save, sender=UserProfile)
def auto_delete_proposal_on_change(sender, instance, **kwargs):
    """
    Deletes old proposal before a new one is uploaded.
    """
    if not instance.pk:
        return
    try:
        old_file = UserProfile.objects.get(pk=instance.pk).accepted_proposal_pdf
        old_file_path = old_file.path
    except UserProfile.DoesNotExist:
        return
    except ValueError:
        return
    new_file = instance.accepted_proposal_pdf
    if not old_file == new_file:
        if os.path.isfile(old_file_path):
            os.remove(old_file_path)


# Add Google Calendar when new Timeline is created
@receiver(models.signals.post_save, sender=Timeline)
def add_calendar(sender, instance, **kwargs):
    instance.add_calendar()


# Add new Event to Google Calendar
@receiver(models.signals.post_save, sender=Event)
def event_add_to_calendar(sender, instance, **kwargs):
    instance.add_to_calendar()


# Publish the event to Github pages
@receiver(models.signals.post_save, sender=Event)
def event_publish_to_github_pages(sender, instance, **kwargs):
    s = Scheduler.objects.filter(
        command="update_site_template",
        data=json.dumps({"template": "deadlines.html"}),
        success=None,
    ).all()
    if len(s) == 0:
        time = timezone.now() + timezone.timedelta(minutes=5)
        Scheduler.objects.create(
            command="update_site_template",
            data=json.dumps({"template": "deadlines.html"}),
            activation_date=time,
        )


# Delete Event from Calendar when obj is deleted
@receiver(models.signals.pre_delete, sender=Event)
def event_delete_from_calendar(sender, instance, **kwargs):
    try:
        instance.delete_from_calendar()
    except Exception:
        pass


# Add respective Schedulers and Builders
# when BlogPostDueDate is created
@receiver(models.signals.post_save, sender=BlogPostDueDate)
def create_schedulers_builders(sender, instance, **kwargs):
    if not instance.add_counter_scheduler:
        instance.create_scheduler()
        instance.create_builders()


# Add new BlogPostDueDate to Google Calendar
@receiver(models.signals.post_save, sender=BlogPostDueDate)
def due_date_add_to_calendar(sender, instance, **kwargs):
    instance.add_to_calendar()


# Add new builder for GsocEndDate
@receiver(models.signals.post_save, sender=GsocEndDate)
def add_revoke_perms_builder(sender, instance, **kwargs):
    Builder.objects.create(
        category="build_revoke_student_perms", activation_date=instance.date
    )


# Add new builder for GsocEndDate
@receiver(models.signals.post_save, sender=GsocEndDate)
def add_revoke_perms_builder(sender, instance, **kwargs):
    Scheduler.objects.create(
        command="archive_gsoc_pages", activation_date=instance.date, data="{}"
    )


# Publish the duedate to Github pages
@receiver(models.signals.post_save, sender=BlogPostDueDate)
def duedate_publish_to_github_pages(sender, instance, **kwargs):
    s = Scheduler.objects.filter(
        command="update_site_template",
        data=json.dumps({"template": "deadlines.html"}),
        success=None,
    ).all()
    if len(s) == 0:
        Scheduler.objects.create(
            command="update_site_template",
            data=json.dumps({"template": "deadlines.html"}),
        )


# Delete BlogPostDueDate from Calendar when obj is deleted
@receiver(models.signals.pre_delete, sender=BlogPostDueDate)
def due_date_delete_from_calendar(sender, instance, **kwargs):
    try:
        instance.delete_from_calendar()
    except Exception:
        pass


# Add Send RegLink Schedulers when RegLink is created
@receiver(models.signals.post_save, sender=RegLink)
def create_send_reglink_schedulers(sender, instance, **kwargs):
    if instance.scheduler is None and instance.send_notifications:
        instance.create_scheduler()


# Add Send RegLink Reminder Schedulers when RegLink is created
@receiver(models.signals.post_save, sender=RegLink)
def create_send_reg_reminder_schedulers(sender, instance, **kwargs):
    if instance.reminder is None and instance.send_notifications:
        instance.create_reminder()


# Add Send Comment Notification
@receiver(models.signals.post_save, sender=Comment)
def send_comment_notification(sender, instance, **kwargs):
    instance.send_notifications()


# Decrease Blog Counter when new Article is created
@receiver(models.signals.pre_save, sender=Article)
def decrease_blog_counter(sender, instance, **kwargs):
    if not instance.pk:
        section = instance.app_config
        up = UserProfile.objects.get(app_config=section)
        if up.current_blog_count > 0:
            up.current_blog_count -= 1
            print("Decreasing", up.current_blog_count)
            up.save()


# Add ArticleReveiw object when new Article is created
@receiver(models.signals.post_save, sender=Article)
def add_review(sender, instance, **kwargs):
    ar = ArticleReview.objects.filter(article=instance).all()
    if not ar:
        ArticleReview.objects.create(article=instance)

    if ar:
        ar = ar.first()
        ar.is_reviewed = False
        ar.save()


# Add BlogPostHistory object when new Article is created
@receiver(models.signals.post_save, sender=Article)
def add_history(sender, instance, **kwargs):
    BlogPostHistory.objects.create(article=instance, content=instance.lead_in)
