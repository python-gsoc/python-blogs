import os
import re

from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.validators import validate_email

import phonenumbers

class Scheduler(models.Model):
    commands = (
        ('send_email', 'send_email'),
        ('send_irc_msg', 'send_irc_msg')
    )
    
    id = models.AutoField(primary_key=True)
    command = models.CharField(name='command', max_length=20, choices=commands)
    data = models.TextField(name='data')
    success = models.BooleanField(name='success', null=True)
    last_error = models.TextField(name='last_error', null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.command


def is_student(self):
    try:
        self.userprofile_set.get(role=3)
        return True
    except UserProfile.DoesNotExist:
        return False
auth.models.User.add_to_class('is_student', is_student)

def student_profile(self):
    try:
        return self.userprofile_set.get(role=3)
    except UserProfile.DoesNotExist:
        return None
auth.models.User.add_to_class('student_profile', student_profile)

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
        quick_phone_pattern = re.compile(r'\+?(?:[0-9]?){6,14}[0-9]')
        phone_numbers = re.findall(quick_phone_pattern, text)
        phone_numbers = [''.join(x) for x in phone_numbers]
        possible_phone_numbers = []
        for phone_number in phone_numbers:
            added = False
            try:
                phone_number_parsed = phonenumbers.parse(phone_number, None)
                if phone_number and phone_number_parsed and phonenumbers.is_possible_number(phone_number_parsed):
                    added = True
                    possible_phone_numbers.append(phone_number)
            except:
                if not added and 10 <= len(phone_number) <= 11:
                    possible_phone_numbers.append(phone_number)
        return possible_phone_numbers
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