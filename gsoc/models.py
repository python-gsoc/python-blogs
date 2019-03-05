import os

from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver

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


class SubOrg(models.Model):
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    gsoc_year = models.IntegerField(name='gsoc_year')

    def __str__(self):
        return str(self.gsoc_year)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gsoc_year = models.ManyToManyField(GsocYear, blank=True)
    suborg_full_name = models.ManyToManyField(SubOrg, blank=True)
    is_student = models.BooleanField(default=True)
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

def suborg_full_name(self):
    try:
        user_profile = UserProfile.objects.get(user=self.id)
        return user_profile.suborg_full_name.all()
    except SubOrg.DoesNotExist:
        return None


def gsoc_year(self):
    try:
        user_profile = UserProfile.objects.get(user=self.id)
        return user_profile.gsoc_year.all()
    except GsocYear.DoesNotExist:
        return None


auth.models.User.add_to_class('suborg_full_name', suborg_full_name)
auth.models.User.add_to_class('gsoc_year', gsoc_year)
