from .models import GsocYear, UserProfile

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission

from cms.api import add_plugin
from cms.utils import permissions
from cms.wizards.forms import BaseFormMixin
from cms.wizards.wizard_pool import wizard_pool

from djangocms_text_ckeditor.html import clean_html

from aldryn_newsblog.models import Article

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.cms_wizards import (
    NewsBlogArticleWizard,
    get_published_app_configs,
    newsblog_article_wizard,
    )

from parler.forms import TranslatableModelForm


def user_has_add_permission(self, user, **kwargs):
    """
    Return True if the current user has permission to add an article.
    :param user: The current user
    :param kwargs: Ignored here
    :return: True if user has add permission, else False
    """
    # No one can create an Article, if there is no app_config yet.
    num_configs = get_published_app_configs()
    if not num_configs:
        return False

    # Ensure user has permission to create articles.
    if user.student_profile() is not None:
        add_perm = Permission.objects.filter(codename="add_article").first()
        if add_perm in user.user_permissions.all():
            return True

    if user.is_superuser:
        return True

    # By default, no permission.
    return False


NewsBlogArticleWizard.user_has_add_permission = user_has_add_permission


class CreateNewsBlogArticleForm(BaseFormMixin, TranslatableModelForm):
    """
    The ModelForm for the NewsBlog article wizard. Note that Article has a
    number of translated fields that we need to access, so, we use
    TranslatableModelForm
    """

    class Meta:
        model = Article
        fields = ["title", "lead_in", "app_config"]
        # The natural widget for app_config is meant for normal Admin views and
        # contains JS to refresh the page on change. This is not wanted here.
        widgets = {"app_config": forms.Select()}

    def __init__(self, **kwargs):
        super(CreateNewsBlogArticleForm, self).__init__(**kwargs)

        # If there's only 1 (or zero) app_configs, don't bother show the
        # app_config choice field, we'll choose the option for the user.
        get_published_app_configs()

        gsoc_year = GsocYear.objects.first()
        student_role = {i[1]: i[0] for i in UserProfile.ROLES}['Student']
        userprofiles = self.user.userprofile_set.filter(gsoc_year=gsoc_year,
                                                        role=student_role)

        if self.user.is_superuser:
            userprofiles = UserProfile.objects.all()

        app_config_choices = []
        for profile in userprofiles:
            app_config_choices.append(
                (profile.app_config.pk, profile.app_config.get_app_title())
                )

        self.fields["app_config"] = forms.ChoiceField(
            label=_("Section"), required=True, choices=app_config_choices
            )

    def clean(self):
        cd = self.cleaned_data
        app_config = NewsBlogConfig.objects.get(pk=self.cleaned_data["app_config"])
        cd["app_config"] = app_config
        return cd

    def save(self, commit=True):
        article = super(CreateNewsBlogArticleForm, self).save(commit=False)
        article.owner = self.user
        article.is_published = True
        article.save()
        return article


wizard_pool.unregister(newsblog_article_wizard)

newsblog_article_wizard = NewsBlogArticleWizard(
    title=_(u"New news/blog article"),
    weight=200,
    form=CreateNewsBlogArticleForm,
    description=_(u"Create a new news/blog article."),
    )

wizard_pool.register(newsblog_article_wizard)
