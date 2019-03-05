from django.contrib import auth
from django.db import models
from django.contrib.auth.models import User


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
