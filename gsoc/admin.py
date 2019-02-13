from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile
from .forms import UserProfileForm


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
