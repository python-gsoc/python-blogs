from .models import (UserProfile, RegLink, UserDetails, Scheduler, PageNotification, AddUserLog,
                     BlogPostDueDate, Builder, Timeline, ArticleReview, Event, SubOrgDetails,
                     GsocEndDate, Comment, SendEmail, BlogPostHistory, GsocYear, SubOrg)
from .forms import (UserProfileForm, UserDetailsForm, RegLinkForm, BlogPostDueDateForm, EventForm,
                    GsocEndDateForm)


from django.contrib.auth.models import User
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.urls import reverse

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
        # self.actions = None
        form = ori_get_form(self, request, obj, **kwargs)
        if is_request_by_student:
            self.actions = None
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
        super(ArticleAdmin, self).delete_model(request, obj)
    else:
        raise PermissionDenied()


def Article_get_queryset(self, request):
    user = request.user
    qs = Article.objects.all()

    if not user.is_superuser:
        userprofiles = user.userprofile_set.all()
        app_configs = []
        for profile in userprofiles:
            app_configs.append(profile.app_config)
        qs = qs.filter(app_config__in=app_configs)

    return qs


def Article_get_actions(self, request):
    actions = super(ArticleAdmin, self).get_actions(request)
    if not request.user.is_superuser:
        return []
    else:
        return actions


ArticleAdmin.save_model = Article_save_model
ArticleAdmin.delete_model = Article_delete_model
ArticleAdmin.get_queryset = Article_get_queryset
ArticleAdmin.get_form = article_get_form()
ArticleAdmin.add_view = Article_add_view
ArticleAdmin.change_view = Article_change_view
ArticleAdmin.get_actions = Article_get_actions

admin.site.unregister(Article)
admin.site.register(Article, ArticleAdmin)


def send_reminder(self, request, queryset):
    for reglink in queryset:
        reglink.create_reminder(trigger_time=timezone.now())


send_reminder.short_description = 'Send reminders'


class RegLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'is_sent',
                           'adduserlog', 'has_scheduler', 'has_reminder')}),
        ("Configure user to be registered",
            {'fields': (
                "user_role",
                "user_suborg",
                "user_gsoc_year",
                "email",
                )}),
        )
    readonly_fields = (
        'url',
        'adduserlog',
        'is_sent',
        'adduserlog',
        'has_scheduler',
        'has_reminder'
        )
    list_display = ('reglink_id', 'email', 'is_used', 'is_sent', 'has_reminder', 'created_at')
    list_filter = [
        'is_used',
        'created_at',
        ]
    actions = [send_reminder]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj and obj.is_used:
            readonly_fields += (
                "user_role",
                "user_suborg",
                "user_gsoc_year",
                'email',
                )

        return readonly_fields


admin.site.register(RegLink, RegLinkAdmin)


def rerun_scheduler(self, request, queryset):
    for scheduler in queryset:
        Scheduler.objects.create(command=scheduler.command,
                                 data=scheduler.data)


rerun_scheduler.short_description = 'Rerun schedulers'


class SchedulerAdmin(admin.ModelAdmin):
    list_display = ('command', 'short_data', 'success', 'last_error', 'created')
    list_filter = ('command', 'success')
    sortable_by = ('created', 'last_error')
    actions = [rerun_scheduler]

    def short_data(self, obj):
        return '{}...'.format(obj.data[:50])


admin.site.register(Scheduler, SchedulerAdmin)


class HiddenUserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'gsoc_year', 'suborg_full_name', 'proposal_confirmed',
                    'hidden', 'reminder_disabled', 'current_blog_count')
    list_filter = ('hidden', 'reminder_disabled')
    readonly_fields = ('user', 'role', 'gsoc_year', 'accepted_proposal_pdf', 'blog_link',
                       'proposal_confirmed', 'current_blog_count', 'github_handle')
    fieldsets = (
        ('Unhide', {
            'fields': ('hidden', 'reminder_disabled')
            }),
        ('User Profile Details', {
            'fields': ('user', 'role', 'gsoc_year', 'accepted_proposal_pdf', 'proposal_confirmed',
                       'blog_link', 'current_blog_count', 'github_handle')
            })
        )

    def blog_link(self, obj):
        ns = obj.app_config.namespace
        page = Page.objects.get(application_namespace=ns, publisher_is_draft=False)
        url = page.get_absolute_url()
        return mark_safe(f'<a href="{url}">{ns}</a>')

    def email(self, obj):
        return obj.user.email

    def get_queryset(self, request):
        return UserProfile.all_objects.all()


admin.site.register(UserProfile, HiddenUserProfileAdmin)


class PageNotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'page')
    list_filter = ('user', 'page')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(PageNotificationAdmin, self).save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fieldsets = (
                (None, {
                    'fields': ('user', 'page', 'message')
                    }), )
        else:
            fieldsets = ((None, {'fields': ('page', 'message')}), )

        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "page":
            kwargs['queryset'] = Page.objects.filter(publisher_is_draft=True)
            if not request.user.is_superuser:
                pp = PagePermission.objects.filter(user=request.user)
                pages = [_.page.pk for _ in pp]
                kwargs['queryset'] = kwargs['queryset'].filter(pk__in=pages)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(PageNotification, PageNotificationAdmin)


class RegLinkInline(admin.TabularInline):
    model = RegLink
    form = RegLinkForm
    extra = 1


class AddUserLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'used_stat')
    readonly_fields = ('log_id', )
    inlines = (RegLinkInline, )
    change_form_template = 'admin/adduserlog_change_form.html'

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['years'] = GsocYear.objects.all()
        extra_context['suborgs'] = SubOrg.objects.all()
        extra_context['roles'] = [(0, 'Others'), (1, 'Suborg Admin'), (2, 'Mentor'), (3, 'Student')]
        return super().changeform_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    def used_stat(self, obj):
        _all = len(RegLink.objects.filter(adduserlog=obj))
        _used = len(RegLink.objects.filter(adduserlog=obj, is_used=True))
        return '{}/{}'.format(_used, _all)


admin.site.register(AddUserLog, AddUserLogAdmin)


def rerun_builder(self, request, queryset):
    for builder in queryset:
        Builder.objects.create(category=builder.category,
                               data=builder.data)


rerun_builder.short_description = 'Rerun builders'


class BuilderAdmin(admin.ModelAdmin):
    list_display = ('category', 'short_data', 'built', 'last_error')
    list_filter = ('category', 'built')
    sortable_by = ('last_error')
    actions = [rerun_builder]

    def short_data(self, obj):
        return '{}...'.format(obj.data[:50])


admin.site.register(Builder, BuilderAdmin)


class BlogPostDueDateInline(admin.TabularInline):
    model = BlogPostDueDate
    form = BlogPostDueDateForm


class EventInline(admin.TabularInline):
    model = Event
    form = EventForm


class GsocEndDateInline(admin.TabularInline):
    model = GsocEndDate
    form = GsocEndDateForm


class TimelineAdmin(admin.ModelAdmin):
    list_display = ('gsoc_year', )
    exclude = ('calendar_id', )
    inlines = (BlogPostDueDateInline, EventInline, GsocEndDateInline)


admin.site.register(Timeline, TimelineAdmin)


class ArticleReviewAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'article_link', 'is_reviewed', 'last_reviewed_by')
    list_filter = ('last_reviewed_by', 'is_reviewed')
    fields = ('article', 'author', 'article_link', 'lead', 'is_reviewed', 'last_reviewed_by')
    change_form_template = 'admin/article_review_change_form.html'

    def lead(self, obj):
        return obj.article.lead_in

    def author(self, obj):
        return obj.article.owner

    def article_link(self, obj):
        url = reverse('{}:article-detail'.format(obj.article.app_config.namespace),
                       args=[obj.article.slug])
        return mark_safe('<a href="{}" target="_blank">Goto Article</a>'.format(url))

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ArticleReview, ArticleReviewAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    fields = ('title', 'start_date', 'end_date', 'timeline', 'calendar_link')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Event, EventAdmin)


class SubOrgDetailsAdmin(admin.ModelAdmin):
    list_display = ('suborg_name', 'gsoc_year', 'changed', 'accepted')
    list_filter = ('gsoc_year', 'changed')
    # fields = ('last_message', )
    readonly_fields = (
        'gsoc_year', 'suborg_admin_email', 'past_gsoc_experience', 'past_years',
        'suborg_in_past', 'applied_but_not_selected', 'year_of_start',
        'source_code', 'docs', 'anything_else', 'suborg_name', 'description',
        'logo', 'primary_os_license', 'ideas_list', 'chat', 'mailing_list', 'twitter_url',
        'blog_url', 'link', 'accepted', 'changed', 'last_reviewed_at', 'last_reviewed_by',
        'created_at', 'updated_at',
    )
    fieldsets = (
        (
            'Details', {
                'fields': (
                    'gsoc_year', 'suborg_admin_email',
                    'past_gsoc_experience', 'past_years',
                    'suborg_in_past', 'applied_but_not_selected',
                    'year_of_start', 'source_code', 'docs', 'anything_else',
                    'suborg_name', 'description',
                    'logo', 'primary_os_license', 'ideas_list', 'chat',
                    'mailing_list', 'twitter_url',
                    'blog_url', 'link', 'changed', 'accepted',
                    'last_reviewed_at', 'last_reviewed_by',
                    'created_at', 'updated_at',
                )
            }
        ),
        ('Review', {'fields': ('last_message', )})
    )
    change_form_template = 'admin/suborg_details_change_form.html'

    def save_model(self, request, obj, form, change):
        obj.changed = False
        obj.last_reviewed_at = timezone.now()
        obj.last_reviewed_by = request.user
        obj.send_review()
        super(SubOrgDetailsAdmin, self).save_model(request, obj, form, change)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(SubOrgDetails, SubOrgDetailsAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'article', 'content')

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Comment, CommentAdmin)


class SendEmailAdmin(admin.ModelAdmin):
    list_display = ('to', 'to_group', 'subject')
    exclude = ('scheduler', )

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SendEmail, SendEmailAdmin)


class BlogPostHistoryAdmin(admin.ModelAdmin):
    list_display = ('article', 'timestamp')
    list_filter = ('article', )
    fields = ('article', 'content_safe', 'timestamp')

    def has_change_permission(self, request, obj=None):
        return False

    def content_safe(self, obj):
        return mark_safe(obj.content)


admin.site.register(BlogPostHistory, BlogPostHistoryAdmin)


class GsocYearAdmin(admin.ModelAdmin):
    list_display = ('gsoc_year', )


admin.site.register(GsocYear, GsocYearAdmin)
