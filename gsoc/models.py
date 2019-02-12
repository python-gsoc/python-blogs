from django.db import models
from django.contrib.auth.models import AbstractUser


class SubOrg(models.Model):
    suborg_name = models.CharField(name='suborg_name', max_length=80)

    def __str__(self):
        return self.suborg_name


class GsocYear(models.Model):
    gsoc_year = models.IntegerField(name='gsoc_year')

    def __str__(self):
        return self.gsoc_year


class User(AbstractUser):
    gsoc_year = models.ForeignKey(GsocYear, on_delete=models.SET_NULL, null=True)
    suborg_full_name = models.ForeignKey(SubOrg, on_delete=models.SET_NULL, null=True)



# def suborg_full_name(self):
#     try:
#         return SubOrg.objects.get(user=self.id)
#     except SubOrg.DoesNotExist:
#         return None
#
#
# def gsoc_year(self):
#     try:
#         return GsocYear.objects.get(user=self.id)
#     except GsocYear.DoesNotExist:
#         return None
#
#
# auth.models.User.add_to_class('suborg_full_name', suborg_full_name)
# auth.models.User.add_to_class('gsoc_year', gsoc_year)
