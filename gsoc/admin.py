from .models import UserDetails
from .forms import UserDetailsForm
from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from .models import UserProfile, RegLink
from .forms import UserProfileForm
from aldryn_people.models import Person
from aldryn_newsblog.admin import ArticleAdmin
from aldryn_newsblog.models import Article
from aldryn_newsblog.cms_appconfig import NewsBlogConfig


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    form = UserProfileForm


class UserDetailsInline(admin.TabularInline):
    model = UserDetails
    form = UserDetailsForm


class UserAdmin(DjangoUserAdmin):
    inlines = [UserDetailsInline, UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

def article_get_form():
    """
    Makes some admin-only fields readonly or hidden for students.
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
                        'publishing_date',
                        'is_published',
                        'is_featured',
                        'featured_image',
                        'lead_in',
                    )}),
                (_('Meta Options'),
                 {'classes': ('collapse',),
                  'fields':()}),
                (_('Advanced Settings'),
                 {'classes': ('collapse',),
                  'fields': ()}),
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
                'owner',
            )
        return form
    return return_func

def Article_add_view(self, request, *args, **kwargs):
    is_student_request = request.user.student_profile() is not None
    data = request.GET.copy()
    post_data = request.POST.copy()
    try:
        person = Person.objects.get(user=request.user)
        data['author'] = person.pk
    except Person.DoesNotExist:
        pass
    if is_student_request:
        timenow = timezone.now()
        try:
            person = Person.objects.get(user=request.user)
            post_data['author'] = person.pk
        except Person.DoesNotExist:
            person = Person.objects.create(user=request.user)
            post_data['author'] = person.pk
        try:
            data['app_config'] = str(NewsBlogConfig.objects.first().pk)
            post_data['app_config'] = str(NewsBlogConfig.objects.first().pk)
            print(data['app_config'])
        except NewsBlogConfig.DoesNotExist:
            pass
        post_data['publishing_date_0'] = f'{str(timenow.year)}-{str(timenow.month).zfill(2)}-{str(timenow.day).zfill(2)}'
        post_data['initial-publishing_date_0'] = f'{str(timenow.year)}-{str(timenow.month).zfill(2)}-{str(timenow.day).zfill(2)}'
        post_data['publishing_date_1'] = f'{str(timenow.hour).zfill(2)}:{str(timenow.minute).zfill(2)}:{str(timenow.second).zfill(2)}'
        post_data['initial-publishing_date_1'] = f'{str(timenow.hour).zfill(2)}:{str(timenow.minute).zfill(2)}:{str(timenow.second).zfill(2)}'
        post_data['owner'] = request.user.pk
        post_data['slug'] = ''
        post_data['meta_title'] = ''
        post_data['meta_description'] = ''
        post_data['meta_keywords'] = ''
        post_data['tags'] = ''
        post_data['related'] = ''
        post_data['featured_image'] = ''
        post_data['is_featured'] = ''
    request.GET = data
    request.POST = post_data
    return super(ArticleAdmin, self).add_view(request, *args, **kwargs)

ArticleAdmin.get_form = article_get_form()
ArticleAdmin.add_view = Article_add_view

admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)

def make_used(modeladmin, request, queryset):
    queryset.update(is_used=True)

make_used.short_description = _(
    "Make the RegLink used.")


def make_unused(modeladmin, request, queryset):
    queryset.update(is_used=False)

make_unused.short_description = _(
    "Make the RegLink link unused.")


class RegLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'is_used')}),
    )
    readonly_fields = (
        'url',
    )
    list_display = ('reglink_id', 'url', 'is_used', 'created_at')
    list_filter = [
        'is_used',
        'created_at',
    ]

    actions = (
        make_used, make_unused,
    )


admin.site.register(RegLink, RegLinkAdmin)
