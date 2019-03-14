from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile
from .forms import UserProfileForm
from aldryn_newsblog.admin import ArticleAdmin
from aldryn_newsblog.models import Article
from aldryn_people.models import Person

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm


class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


"""
Make some admin-only fields not editable for students,
and give some fields initial value.
"""

def article_get_form(self, request, obj=None, **kwargs):
    """
    Gives some initial form value for students.
    """
    is_request_by_student = request.user.student_profile() is not None
    form = super(ArticleAdmin, self).get_form(request, obj, **kwargs)
    if is_request_by_student is False:
        return form
    try:
        default_author = Person.objects.get(user=request.user)
    except Person.DoesNotExist:
        default_author = None
    if default_author is not None:
        form.base_fields['related'].initial = default_author
    return form
def article_get_readonly_fields(self, request, obj=None):
    """
    Makes some admin-only fields readonly for students.
    """
    student_readonly_fields = [
        'author',
        'publishing_date',
        'is_featured',
        'featured_image',
    ]
    is_request_by_student = request.user.student_profile() is not None
    if not is_request_by_student:
        return self.readonly_fields
    else:
        return student_readonly_fields + list(self.readonly_fields)
# ArticleAdmin.get_form = article_get_form
ArticleAdmin.get_readonly_fields = article_get_readonly_fields
admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)
