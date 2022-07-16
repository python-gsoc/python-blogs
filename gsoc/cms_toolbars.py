from cms.cms_toolbars import (
    BasicToolbar,
    PageToolbar,
    ADMIN_MENU_IDENTIFIER,
    ADMINISTRATION_BREAK,
    USER_SETTINGS_BREAK,
    TOOLBAR_DISABLE_BREAK,
    SHORTCUTS_BREAK,
    CLIPBOARD_BREAK,
)
from cms.utils.page_permissions import (
    user_can_change_page,
    user_can_delete_page,
    user_can_publish_page,
)
from cms.constants import TEMPLATE_INHERITANCE_MAGIC
from cms.utils.conf import get_cms_setting
from cms.utils.urlutils import add_url_parameters, admin_reverse
from cms.utils import get_language_from_request, page_permissions

from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language_from_request
from django.urls import reverse

from aldryn_translation_tools.utils import get_admin_url, get_object_from_request
from aldryn_newsblog.models import Article
from aldryn_newsblog.cms_toolbars import NewsBlogToolbar

from cms.models import Page

from gsoc.models import ArticleReview


# identifiers
PAGE_MENU_IDENTIFIER = 'page'
PAGE_MENU_ADD_IDENTIFIER = 'add_page'
PAGE_MENU_FIRST_BREAK = 'Page Menu First Break'
PAGE_MENU_SECOND_BREAK = 'Page Menu Second Break'
PAGE_MENU_THIRD_BREAK = 'Page Menu Third Break'
PAGE_MENU_FOURTH_BREAK = 'Page Menu Fourth Break'
PAGE_MENU_LAST_BREAK = 'Page Menu Last Break'
TEMPLATE_MENU_BREAK = 'Template Menu Break'


def add_admin_menu(self):
    if not self._admin_menu:
        self._admin_menu = self.toolbar.get_or_create_menu(
            ADMIN_MENU_IDENTIFIER, self.current_site.name
        )

        user = getattr(self.request, "user", None)

        if user and user.is_superuser:
            # Users button
            self._admin_menu.add_sideframe_item(
                _("User Profiles"), url=admin_reverse("gsoc_userprofile_changelist")
            )

        # sites menu
        sites_queryset = Site.objects.order_by("name")

        if len(sites_queryset) > 1:
            sites_menu = self._admin_menu.get_or_create_menu("sites", _("Sites"))
            sites_menu.add_sideframe_item(
                _("Admin Sites"), url=admin_reverse("sites_site_changelist")
            )
            sites_menu.add_break(ADMINISTRATION_BREAK)
            for site in sites_queryset:
                sites_menu.add_link_item(
                    site.name,
                    url="http://%s" % site.domain,
                    active=site.pk == self.current_site.pk,
                )

        # admin
        if user and user.is_superuser:
            self._admin_menu.add_sideframe_item(
                _("Administration"), url=admin_reverse("index")
            )

        # scheduler
        if user and user.is_superuser:
            self._admin_menu.add_sideframe_item(
                _("Schedulers"), url=admin_reverse("gsoc_scheduler_changelist")
            )
            self._admin_menu.add_sideframe_item(
                _("Builders"), url=admin_reverse("gsoc_builder_changelist")
            )
            self._admin_menu.add_sideframe_item(
                _("Review Article"), url=admin_reverse("gsoc_articlereview_changelist")
            )
            self._admin_menu.add_sideframe_item(
                _("Timeline"), url=admin_reverse("gsoc_timeline_changelist")
            )
            self._admin_menu.add_sideframe_item(
                _("Send Email"), url=admin_reverse("gsoc_sendemail_add")
            )
            self._admin_menu.add_sideframe_item(
                _("Suborg Applications"),
                url=admin_reverse("gsoc_suborgdetails_changelist"),
            )
            self._admin_menu.add_modal_item(
                name="Add Users",
                url=admin_reverse("gsoc_adduserlog_add"),
                on_close=None,
            )

        if user and not user.is_current_year_student():
            self._admin_menu.add_link_item(
                _("New Suborg Application"), reverse("suborg:register_suborg")
            )
            self._admin_menu.add_link_item(
                _("Manage Suborg Application"), reverse("suborg:application_list")
            )

        if user and user.is_superuser:
            # Export button
            self._admin_menu.add_sideframe_item(
                _("Export Mentors"), reverse("export_view")
            )

        self._admin_menu.add_break(ADMINISTRATION_BREAK)

        # cms users settings
        self._admin_menu.add_sideframe_item(
            _("User settings"), url=admin_reverse("cms_usersettings_change")
        )
        self._admin_menu.add_break(USER_SETTINGS_BREAK)
        # clipboard
        if user and user.is_superuser and self.toolbar.edit_mode_active:
            # True if the clipboard exists and there's plugins in it.
            clipboard_is_bound = self.toolbar.clipboard_plugin

            self._admin_menu.add_link_item(
                _("Clipboard..."),
                url="#",
                extra_classes=["cms-clipboard-trigger"],
                disabled=not clipboard_is_bound,
            )
            self._admin_menu.add_link_item(
                _("Clear clipboard"),
                url="#",
                extra_classes=["cms-clipboard-empty"],
                disabled=not clipboard_is_bound,
            )
            self._admin_menu.add_break(CLIPBOARD_BREAK)

        # logout
        self.add_logout_button(self._admin_menu)


def add_goto_blog_button(self):
    user = getattr(self.request, "user", None)
    if user and user.is_current_year_student():
        profile = user.student_profile()
        ns = profile.app_config.namespace
        page = Page.objects.get(application_namespace=ns, publisher_is_draft=False)
        url = page.get_absolute_url()
        self.toolbar.add_button(_("My Blog"), url, side=self.toolbar.RIGHT)


def populate(self):
    if not self.page:
        self.init_from_request()
        self.clipboard = self.request.toolbar.user_settings.clipboard
        self.add_admin_menu()
        self.add_language_menu()
        self.add_goto_blog_button()


BasicToolbar.add_admin_menu = add_admin_menu
BasicToolbar.add_goto_blog_button = add_goto_blog_button
BasicToolbar.populate = populate


def add_page_menu(self):
    return None


PageToolbar.add_page_menu = add_page_menu


def populate(self):
    config = self._NewsBlogToolbar__get_newsblog_config()
    if not config:
        # Do nothing if there is no NewsBlog app_config to work with
        return

    user = getattr(self.request, "user", None)
    try:
        view_name = self.request.resolver_match.view_name
    except AttributeError:
        view_name = None

    if user and view_name:
        language = get_language_from_request(self.request, check_path=True)

        # If we're on an Article detail page, then get the article
        if view_name == "{0}:article-detail".format(config.namespace):
            article = get_object_from_request(Article, self.request)
        else:
            article = None

        menu = self.toolbar.get_or_create_menu("newsblog-app", config.get_app_title())

        change_config_perm = user.has_perm("aldryn_newsblog.change_newsblogconfig")
        add_config_perm = user.has_perm("aldryn_newsblog.add_newsblogconfig")
        config_perms = [change_config_perm, add_config_perm]

        change_article_perm = False
        userprofiles = user.userprofile_set.all()

        if user.is_superuser:
            change_article_perm = True
        else:
            for profile in userprofiles:
                if profile.app_config == config:
                    change_perm = Permission.objects.filter(
                        codename="change_article"
                    ).first()
                    if change_perm in user.user_permissions.all():
                        change_article_perm = True
                        break

        add_article_perm = user.is_superuser if article else False
        delete_article_perm = user.is_superuser if article else False

        article_perms = [change_article_perm, add_article_perm, delete_article_perm]

        if change_config_perm:
            url_args = {}
            if language:
                url_args = {"language": language}
            url = get_admin_url(
                "aldryn_newsblog_newsblogconfig_change", [config.pk], **url_args
            )
            menu.add_modal_item(_("Configure addon"), url=url)

        if any(config_perms) and any(article_perms):
            menu.add_break()

        if change_article_perm:
            url_args = {}
            if config:
                url_args = {"app_config__id__exact": config.pk}
            url = get_admin_url("aldryn_newsblog_article_changelist", **url_args)
            menu.add_sideframe_item(_("Article list"), url=url)

        # if add_article_perm:
        #     url_args = {'app_config': config.pk, 'owner': user.pk, }
        #     if language:
        #         url_args.update({'language': language, })
        #     url = get_admin_url('aldryn_newsblog_article_add', **url_args)
        #     menu.add_modal_item(_('Add new article'), url=url)

        if change_article_perm and article:
            url_args = {}
            if language:
                url_args = {"language": language}
            url = get_admin_url(
                "aldryn_newsblog_article_change", [article.pk], **url_args
            )
            menu.add_modal_item(_("Edit this article"), url=url, active=True)

        if change_article_perm and article:
            if article.is_published:
                text = _("Unpublish Article")
                url = reverse("unpublish_article", args=[article.id])
            else:
                text = _("Publish Article")
                url = reverse("publish_article", args=[article.id])

            self.toolbar.add_button(text, url=url, side=self.toolbar.RIGHT)

        if delete_article_perm and article:
            redirect_url = self.get_on_delete_redirect_url(article, language=language)
            url = get_admin_url("aldryn_newsblog_article_delete", [article.pk])
            menu.add_modal_item(
                _("Delete this article"), url=url, on_close=redirect_url
            )

        try:
            article_review = ArticleReview.objects.get(article=article)
            if not article_review.is_reviewed and user.is_superuser:
                url = reverse("review_article", args=[article.id])
                self.toolbar.add_button(
                    _("Mark Reviewed"), url=url, side=self.toolbar.RIGHT
                )
        except ArticleReview.DoesNotExist:
            pass

        try:
            if user.is_superuser:
                url = (
                    f"{admin_reverse('gsoc_blogposthistory_changelist')}"
                    f"?article__id__exact={article.id}"
                )
                self.toolbar.add_sideframe_item(_("View History"), url=url)
        except Exception as e:
            pass


NewsBlogToolbar.populate = populate
