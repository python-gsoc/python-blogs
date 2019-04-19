from .models import UserProfile, RegLink, UserDetails, Scheduler, PageNotification
from .forms import UserProfileForm, UserDetailsForm

from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from aldryn_people.models import Person
from aldryn_newsblog.admin import ArticleAdmin
from aldryn_newsblog.models import Article

from cms.models import Page, PagePermission


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
                # (_('Meta Options'),
                #  {'classes': ('collapse',),
                #   'fields':()}),
                (_('Advanced Settings'),
                 {'classes': ('collapse',),
                  'fields': ('app_config',)}),
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


def Article_change_view(self, request, object_id, *args, **kwargs):
    is_student_request = request.user.student_profile() is not None
    data = request.GET.copy()
    post_data = request.POST.copy()
    try:
        original_article = Article.objects.get(pk=object_id)
    except Article.DoesNotExist:
        return super(ArticleAdmin, self).change_view(request, object_id, *args, **kwargs)
    if is_student_request:
        timenow = original_article.publishing_date
        try:
            person = Person.objects.get(user=request.user)
            post_data['author'] = person.pk
        except Person.DoesNotExist:
            person = Person.objects.create(user=request.user)
            post_data['author'] = person.pk
        post_data['publishing_date_0'] = f'{str(timenow.year)}-{str(timenow.month).zfill(2)}-{str(timenow.day).zfill(2)}'
        post_data['initial-publishing_date_0'] = f'{str(timenow.year)}-{str(timenow.month).zfill(2)}-{str(timenow.day).zfill(2)}'
        post_data['publishing_date_1'] = f'{str(timenow.hour).zfill(2)}:{str(timenow.minute).zfill(2)}:{str(timenow.second).zfill(2)}'
        post_data['initial-publishing_date_1'] = f'{str(timenow.hour).zfill(2)}:{str(timenow.minute).zfill(2)}:{str(timenow.second).zfill(2)}'
        post_data['owner'] = request.user.pk
    request.GET = data
    request.POST = post_data
    return super(ArticleAdmin, self).change_view(request, object_id, *args, **kwargs)


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


def Article_save_model(self, request, obj, form, change):
    # checks whether user has add permission in the current
    # section before adding to the blog
    user = request.user
    has_add_perm = False
    if user.is_superuser:
        has_add_perm = True
    else:
        userprofiles = user.userprofile_set.all()
        for profile in userprofiles:
            if profile.app_config == obj.app_config:
                has_add_perm = True
                break

    if has_add_perm:
        super(ArticleAdmin, self).save_model(request, obj, form, change)
    else:
        raise PermissionDenied()


def Article_delete_model(self, request, obj):
    # checks whether user has delete permission in the current
    # section before adding to the blog
    user = request.user
    has_delete_perm = False
    if user.is_superuser:
        has_delete_perm = True
    else:
        userprofiles = user.userprofile_set.all()
        for profile in userprofiles:
            if profile.app_config == obj.app_config:
                has_delete_perm = True
                break

    if has_delete_perm:
        super(ArticleAdmin, self).delete_model(request, obj, form, change)
    else:
        raise PermissionDenied()


def Article_get_queryset(self, request):
    user = request.user
    qs = Article.objects.all()

    if user.is_superuser:
        return qs
    else:
        userprofiles = user.userprofile_set.all()
        app_configs = []
        for profile in userprofiles:
            app_configs.append(profile.app_config)
        qs = qs.filter(app_config__in=app_configs)
        print(qs)
        return qs


ArticleAdmin.save_model = Article_save_model
ArticleAdmin.delete_model = Article_delete_model
ArticleAdmin.get_queryset = Article_get_queryset
ArticleAdmin.get_form = article_get_form()
ArticleAdmin.add_view = Article_add_view
ArticleAdmin.change_view = Article_change_view

admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)


class RegLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('url',)}),
        ("Configure user to be registered",
            {'fields': (
                "user_role",
                "user_suborg",
                "user_gsoc_year",
                )}),
        )
    readonly_fields = (
        'url',
        )
    list_display = ('reglink_id', 'url', 'is_used', 'created_at')
    list_filter = [
        'is_used',
        'created_at',
        ]

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_used:
            return self.readonly_fields + (
                "user_role",
                "user_suborg",
                "user_gsoc_year",
                )
        else:
            return self.readonly_fields


admin.site.register(RegLink, RegLinkAdmin)


class SchedulerAdmin(admin.ModelAdmin):
    list_display = ('command', 'data', 'success', 'last_error', 'created')
    list_filter = ('command', 'success')
    sortable_by = ('created', 'last_error')


admin.site.register(Scheduler, SchedulerAdmin)


class HiddenUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gsoc_year', 'suborg_full_name', 'hidden')
    list_filter = ('hidden', )
    readonly_fields = ('user', 'role', 'gsoc_year', 'accepted_proposal_pdf', 'app_config')
    fieldsets = (
        ('Unhide', {
            'fields': ('hidden', )
            }),
        ('User Profile Details', {
            'fields': ('user', 'role', 'gsoc_year', 'accepted_proposal_pdf', 'app_config')
            })
        )

    def get_queryset(self, request):
        return UserProfile.all_objects.all()


admin.site.register(UserProfile, HiddenUserProfileAdmin)


class PageNotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'page')
    list_filter = ('user', 'page')

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (None, {
                    'fields': ('user', 'page', 'message')
                    }), )
        else:
            return ((None, {'fields': ('page', 'message')}), )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "page":
            kwargs['queryset'] = Page.objects.filter(publisher_is_draft=True)
            if not request.user.is_superuser:
                pp = PagePermission.objects.filter(user=request.user)
                pages = [_.page.pk for _ in pp]
                kwargs['queryset'] = kwargs['queryset'].filter(pk__in=pages)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(PageNotification, PageNotificationAdmin)
