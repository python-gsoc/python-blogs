from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import UserProfile
from .forms import UserProfileForm
from aldryn_newsblog.admin import ArticleAdmin
from aldryn_newsblog.models import Article

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


def article_get_form():
    """
    Makes some admin-only fields readonly for students.
    """
    ori_get_form = ArticleAdmin.get_form
    ori_fieldsets = None
    ori_readonly_fields = None
    def return_func(self, request, obj=None, **kwargs):
        nonlocal ori_readonly_fields, ori_fieldsets
        is_request_by_student = request.user.student_profile() is not None
        if ori_readonly_fields is None:
            ori_readonly_fields = getattr(self, 'readonly_fields', ()) or ()
        if ori_fieldsets is None:
            ori_fieldsets = getattr(self, 'fieldsets', ()) or ()
        self.readonly_fields = ori_readonly_fields
        self.fieldsets = ori_fieldsets
        form = ori_get_form(self, request, obj, **kwargs)
        if is_request_by_student:
            self.fieldsets = (
                (None, {
                    'fields': (
                        'title',
                        'author',
                        'publishing_date',
                        'is_published',
                        'is_featured',
                        'featured_image',
                        'lead_in',
                    )}),
                (_('Meta Options'), {'classes': ('collapse',), 'fields': ()}),
                (_('Advanced Settings'), {'classes': ('collapse',), 'fields': ()}),
            )
            self.readonly_fields = (
                'author',
                'publishing_date',
                'is_featured',
                'featured_image',
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
                'tags',
                'categories',
                'related',
                'owner',
            )
        return form
    return return_func

ArticleAdmin.get_form = article_get_form()
admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)
