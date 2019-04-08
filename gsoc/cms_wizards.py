from django import forms
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin
from cms.utils import permissions

from djangocms_text_ckeditor.html import clean_html

from aldryn_newsblog.cms_appconfig import NewsBlogConfig
from aldryn_newsblog.cms_wizards import (
    NewsBlogArticleWizard,
    CreateNewsBlogArticleForm,
    get_published_app_configs
)


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
    if user.is_superuser or user.student_profile() is not None:
        return True

    # By default, no permission.
    return False


NewsBlogArticleWizard.user_has_add_permission = user_has_add_permission


CreateNewsBlogArticleForm.Meta.fields = ['title']


def __init__(self, **kwargs):
    super(CreateNewsBlogArticleForm, self).__init__(**kwargs)

    # If there's only 1 (or zero) app_configs, don't bother show the
    # app_config choice field, we'll choose the option for the user.
    app_configs = get_published_app_configs()

    userprofiles = self.user.userprofile_set.all()
    app_config_choices = []
    for profile in userprofiles:
        app_config_choices.append((profile.app_config.pk, profile.app_config.get_app_title()))
    
    self.fields['app_config'] = forms.ChoiceField(
        label=_('Section'),
        required=True,
        choices=app_config_choices
    )


def save(self, commit=True):
    article = super(CreateNewsBlogArticleForm, self).save(commit=False)
    article.owner = self.user
    article.app_config = NewsBlogConfig.objects.filter(pk=self.cleaned_data['app_config']).first()
    article.save()

    # If 'content' field has value, create a TextPlugin with same and add it to the PlaceholderField
    content = clean_html(self.cleaned_data.get('content', ''), False)
    if content and permissions.has_plugin_permission(self.user, 'TextPlugin', 'add'):
        add_plugin(
            placeholder=article.content,
            plugin_type='TextPlugin',
            language=self.language_code,
            body=content,
        )

    return article


CreateNewsBlogArticleForm.__init__ = __init__
CreateNewsBlogArticleForm.save = save
