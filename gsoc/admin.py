from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile,SubOrgForm
from .forms import UserProfileForm


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]

class SubOrgFormAdmin(admin.ModelAdmin):
    list_display = ('user','suborg_admin_email','mentor_email')

admin.site.register(SubOrgForm, SubOrgFormAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
