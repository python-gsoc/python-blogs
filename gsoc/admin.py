from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
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
    ori_readonly_fields = None
    ori_field_sets = None
    def return_func(self, request, obj=None, **kwargs):
        nonlocal ori_readonly_fields, ori_field_sets
        is_request_by_student = request.user.student_profile() is not None
        if ori_readonly_fields is None:
            ori_readonly_fields = self.readonly_fields
        if ori_field_sets is None:
            ori_field_sets = self.__class__.fieldsets
        self.readonly_fields = ori_readonly_fields
        self.__class__.field_sets = ori_field_sets
        if is_request_by_student:
            self.__class__.field_sets = self.__class__.field_sets[0]
            print(self.__class__.field_sets)
        form = ori_get_form(self, request, obj, **kwargs)
        if is_request_by_student:
            self.readonly_fields = [
                'author',
                'publishing_date',
                'is_featured',
                'featured_image',
            ]
        return form
    return return_func
ArticleAdmin.get_form = article_get_form()

admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)
