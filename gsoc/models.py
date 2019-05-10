import os
import re
import datetime
import uuid

from ics import Event

from django.contrib.auth.models import Permission
from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import validate_email
from django.utils import timezone
from django.shortcuts import reverse
from django.conf import settings

from aldryn_apphooks_config.fields import AppHookConfigField

from aldryn_newsblog.cms_appconfig import NewsBlogConfig

from cms.models import Page, PagePermission
from cms import api
from cms.utils.conf import get_cms_setting
from cms.utils.apphook_reload import mark_urlconf_as_changed

import phonenumbers
from phonenumbers.phonenumbermatcher import PhoneNumberMatcher

from gsoc.common.utils.tools import build_send_mail_json
from gsoc.settings import PROPOSALS_PATH

NewsBlogConfig.__str__ = lambda self: self.app_title


class SubOrg(models.Model):
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    class Meta:
        ordering = ['-gsoc_year']
    gsoc_year = models.IntegerField(name='gsoc_year')

    def __str__(self):
        return str(self.gsoc_year)


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(hidden=False)


class UserProfile(models.Model):
    ROLES = (
        (0, 'Others'),
        (1, 'Suborg Admin'),
        (2, 'Mentor'),
        (3, 'Student')
        )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.IntegerField(name='role', choices=ROLES, default=0)
    gsoc_year = models.ForeignKey(GsocYear, on_delete=models.CASCADE, null=True, blank=False)
    suborg_full_name = models.ForeignKey(SubOrg, on_delete=models.CASCADE, null=True, blank=False)
    accepted_proposal_pdf = models.FileField(blank=True, null=True, upload_to=PROPOSALS_PATH)
    app_config = AppHookConfigField(NewsBlogConfig,
                                    verbose_name=_('Section'),
                                    blank=True, null=True,)
    hidden = models.BooleanField(name='hidden', default=False)

    objects = UserProfileManager()
    all_objects = models.Manager()


def has_proposal(self):
    try:
        if self.userprofile_set.get(role=3).accepted_proposal_pdf.path:
            return True

    except BaseException:
        return False


def is_current_year_student(self):
    try:
        profile = self.userprofile_set.get(role=3)
        year = profile.gsoc_year.gsoc_year
        current_year = datetime.datetime.now().year
        return current_year == year
    except UserProfile.DoesNotExist:
        return False


def student_profile(self):
    try:
        # TODO: will raise MultipleObjectsReturned when there are more than
        # one student profiles, fix this
        return self.userprofile_set.get(role=3)
    except UserProfile.DoesNotExist:
        return None


auth.models.User.add_to_class('has_proposal', has_proposal)
auth.models.User.add_to_class('is_current_year_student', is_current_year_student)
auth.models.User.add_to_class('student_profile', student_profile)

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


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    deactivation_date = models.DateTimeField(name='deactivation_date', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'User details'

    def save(self, *args, **kwargs):
        if self.deactivation_date:
            s = Scheduler(command='deactivate_user', data=self.user.pk,
                          activation_date=self.deactivation_date)
            s.save()

        super(UserDetails, self).save(*args, **kwargs)


class Scheduler(models.Model):
    commands = (
        ('send_email', 'send_email'),
        ('send_irc_msg', 'send_irc_msg'),
        ('deactivate_user', 'deactivate_user'),
        )

    id = models.AutoField(primary_key=True)
    command = models.CharField(name='command', max_length=20, choices=commands)
    activation_date = models.DateTimeField(name='activation_date', null=True, blank=True)
    data = models.TextField(name='data')
    success = models.BooleanField(name='success', null=True)
    last_error = models.TextField(name='last_error', null=True, default=None, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.command


class PageNotification(models.Model):
    message = models.TextField(name='message')
    user = models.ForeignKey(User, name='user',
                             on_delete=models.CASCADE)
    page = models.ForeignKey(Page, name='page', related_name='notifications',
                             on_delete=models.CASCADE)
    pubished_page = models.ForeignKey(Page, name='published_page',
                                      related_name='notifications_for_published',
                                      on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.page and self.page.publisher_is_draft:
            page = self.page
            published_page = Page.objects.filter(node_id=page.node_id,
                                                 publisher_is_draft=False).first()
            self.published_page = published_page
            perm = PagePermission.objects.filter(page=page).filter(user=self.user).first()

            if self.user.is_superuser or (perm and perm.can_change):
                super().save(*args, **kwargs)
            else:
                raise ValidationError(message='User does not have permissions on this page')
        else:
            raise ValidationError(message='Add notification on unpublished page')


class ProposalTextValidator:
    def find_all_emails(self, text):
        """
        Returns all emails in the text in a list.
        """
        quick_email_pattern = re.compile("""
        [a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@
        (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?
        """, re.X)
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
        matcher = PhoneNumberMatcher(text, 'US')
        all_numbers = list(iter(matcher))
        all_number_strings = [x.raw_string for x in all_numbers]
        ptn = re.compile(r'\+?[0-9][0-9\(\)\-\ ]{3,}[0-9]', re.A | re.M)
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


validate_proposal_text = ProposalTextValidator()


def gen_uuid_str():
    return str(uuid.uuid4())


class AddUserLog(models.Model):
    class Meta:
        verbose_name = 'Add Users' \
                       '(The invites will be sent to the emails on save)'
        verbose_name_plural = 'Add Users' \
                              '(The invites will be sent to the emails on save)'
    log_id = models.CharField(max_length=36,
                              default=gen_uuid_str)

    def __str__(self):
        return self.log_id


class RegLink(models.Model):
    is_used = models.BooleanField(default=False, editable=False)
    reglink_id = models.CharField(max_length=36, default=gen_uuid_str, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user_role = models.IntegerField(name="user_role",
                                    choices=UserProfile.ROLES, default=0, null=True, blank=False,
                                    )
    user_suborg = models.ForeignKey(SubOrg, name="user_suborg",
                                    on_delete=models.CASCADE, null=True, blank=False)
    user_gsoc_year = models.ForeignKey(GsocYear, name="user_gsoc_year",
                                       on_delete=models.CASCADE, null=True, blank=False)
    adduserlog = models.ForeignKey(AddUserLog, on_delete=models.CASCADE,
                                   null=True, blank=True, related_name='reglinks')
    email = models.CharField(null=False, blank=False,
                             default='', max_length=300, validators=[validate_email])
    scheduler = models.ForeignKey(Scheduler, null=True,
                                  blank=True, on_delete=models.CASCADE, editable=False)

    @property
    def has_scheduler(self):
        return self.scheduler is not None

    @property
    def url(self):
        return f'{reverse("register")}?reglink_id={self.reglink_id}'

    @property
    def is_sent(self):
        return self.scheduler is not None and self.scheduler.success

    def __str__(self):
        sent = self.is_sent
        if sent:
            sent_str = 'Sent.'
        else:
            sent_str = 'Not sent.'
        return f"Register Link {self.url} for {self.email}. {sent_str}"

    def is_usable(self):
        timenow = timezone.now()
        return (not self.is_used) and self.created_at < timenow

    def create_user(self, *args, is_staff=True, **kwargs):
        namespace = str(uuid.uuid4())
        email = kwargs.get('email', self.email)
        user = User.objects.create(*args, is_staff=is_staff,
                                   email=email, **kwargs)
        role = {k: v for v, k in UserProfile.ROLES}
        profile = UserProfile.objects.create(user=user, role=self.user_role,
                                             gsoc_year=self.user_gsoc_year,
                                             suborg_full_name=self.user_suborg)
        if self.user_role != role.get('Student', 3):
            return user

        blogname = f"{user.username}'s Blog"
        app_config = NewsBlogConfig.objects.create(namespace=namespace)
        app_config.app_title = blogname
        app_config.save()
        profile.app_config = app_config
        profile.save()
        blog_list_page = Page.objects.\
            filter(application_namespace='blogs_list').\
            filter(publisher_is_draft=True).first()
        page = api.create_page(blogname,
                               get_cms_setting('TEMPLATES')[0][0],
                               'en', published=True,
                               publication_date=timezone.now(),
                               apphook=app_config.cmsapp,
                               apphook_namespace=namespace,
                               parent=blog_list_page)
        su = User.objects.filter(is_superuser=True).first()
        api.publish_page(page, su, 'en')

        permissions = list()
        permissions.append(Permission.objects.filter(codename='add_article').first())
        permissions.append(Permission.objects.filter(codename='change_article').first())
        permissions.append(Permission.objects.filter(codename='delete_article').first())
        permissions.append(Permission.objects.filter(codename='view_article').first())
        user.user_permissions.set(permissions)

        mark_urlconf_as_changed()
        return user

    def create_scheduler(self, trigger_time=timezone.now()):
        validate_email(self.email)
        scheduler_data = build_send_mail_json(self.email,
                                              template='invite.html',
                                              subject='Your GSoC 2019 invite',
                                              template_data={
                                                  'register_link':
                                                      settings.INETLOCATION +
                                                      self.url})
        s = Scheduler.objects.create(command='send_email',
                                     activation_date=trigger_time,
                                     data=scheduler_data)
        self.scheduler = s
        self.save()


@receiver(models.signals.post_save, sender=RegLink)
def create_send_reglink_schedulers(sender, instance, **kwargs):
    if instance.adduserlog is not None and instance.scheduler is None:
        instance.create_scheduler()


class Event(models.Model):
    gsoc_year = models.ForeignKey(GsocYear, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    groups = models.ManyToManyField(Group, null=True, blank=True)
    users = models.ManyToManyField(User, null=True, blank=True)

    def add_to_calendar(self, cal):
        e = Event()
        e.name = self.title
        e.begin = self.start_date
        if self.end_date:
            e.end = self.end_date
        else:
            e.make_all_day()

        cal.events.append(e)
        return cal
