from django.contrib import auth
from django.contrib.auth.models import User
from django.db import models


class SubOrg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gsoc_year = models.CharField(name='gsoc_year', max_length=5)

    def __str__(self):
        return self.gsoc_year


def suborg_full_name(self):
    try:
        return SubOrg.objects.get(user=self.id)
    except SubOrg.DoesNotExist:
        return None


def gsoc_year(self):
    try:
        return GsocYear.objects.get(user=self.id)
    except GsocYear.DoesNotExist:
        return None


auth.models.User.add_to_class('suborg_full_name', suborg_full_name)
auth.models.User.add_to_class('gsoc_year', gsoc_year)
