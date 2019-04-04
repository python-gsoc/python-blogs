import os
import re
import datetime
import uuid

from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import validate_email
from django.utils import timezone
from django.shortcuts import reverse
from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.models import Article

import phonenumbers
from phonenumbers.phonenumbermatcher import PhoneNumberMatcher


class SubOrg(models.Model):
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    gsoc_year = models.IntegerField(name='gsoc_year')

    def __str__(self):
        return str(self.gsoc_year)


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
    accepted_proposal_pdf = models.FileField(blank=True, null=True)
    app_config = AppHookConfigField(NewsBlogConfig, verbose_name=_('Section'), blank=True, null=True)


def has_proposal(self):
    try:
        self.userprofile_set.get(role=3).accepted_proposal_pdf.path
        return True
    except:
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
    last_error = models.TextField(name='last_error', null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.command


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
            except:
                pass
        return real_emails
    def find_all_possible_phone_numbers(self, text):
        """
        Returns all possible phone numbers in a list.
        """
        matcher = PhoneNumberMatcher(text, 'US')
        all_numbers = list(iter(matcher))
        all_number_strings = [x.raw_string for x in all_numbers]
        ptn = re.compile(r'\+?[0-9][0-9\(\)\-\ ]{3,}[0-9]', re.A| re.M)
        maybe_numbers = re.findall(ptn, text)
        for maybe_number in maybe_numbers:
            if maybe_number in all_number_strings:
                continue
            try:
                maybe_number_parsed = phonenumbers.parse(maybe_number)
                if phonenumbers.is_possible_number(maybe_number_parsed):
                    all_number_strings.append(maybe_number)
            except:
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
                                          on_delete=models.CASCADE,  null=True, blank=False)
    @property
    def url(self):
        return f'{reverse("register")}?reglink_id={self.reglink_id}'
    def is_usable(self):
        timenow = timezone.now()
        return (not self.is_used) and self.created_at < timenow
    def create_user(self, *args, is_staff=True, **kwargs):
        user = User.objects.create(*args, is_staff=is_staff, **kwargs)
        UserProfile.objects.create(user=user, role=self.user_role, gsoc_year=self.user_gsoc_year, suborg_full_name=self.user_suborg)
        return user

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=200)
    author_mail = models.CharField(max_length=50)
    author_site = models.CharField(max_length=50)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    def approve(self):
        self.approved_comment = True
        self.save()
    def __str__(self):
        return self.text

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    author_name = models.CharField(max_length=200)
    author_mail = models.CharField(max_length=50)
    author_site = models.CharField(max_length=50)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)
    def approve(self):
        self.approved_comment = True
        self.save()
    def __str__(self):
        return self.text
