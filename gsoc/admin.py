from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import GsocYear, SubOrg


class GsocYearInline(admin.TabularInline):
    model = GsocYear


class SuborgInline(admin.TabularInline):
    model = SubOrg


class UserAdmin(DjangoUserAdmin):
    inlines = [GsocYearInline, SuborgInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
