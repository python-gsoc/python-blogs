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
    user = getattr(self.request, "user", None)
    if user and user.is_superuser:
        if self.page:
            edit_mode = self.toolbar.edit_mode_active
            refresh = self.toolbar.REFRESH_PAGE
            can_change = user_can_change_page(
                user=self.request.user,
                page=self.page,
                site=self.current_site,
            )

            # menu for current page
            # NOTE: disabled if the current path is "deeper" into the
            # application's url patterns than its root. This is because
            # when the Content Manager is at the root of the app-hook,
            # some of the page options still make sense.
            current_page_menu = self.toolbar.get_or_create_menu(
                PAGE_MENU_IDENTIFIER,
                _('Page'), position=1,
                disabled=self.in_apphook() and not self.in_apphook_root()
            )

            new_page_params = {'edit': 1}
            new_sub_page_params = {'edit': 1, 'parent_node': self.page.node_id}

            if self.page.is_page_type:
                add_page_url = admin_reverse('cms_pagetype_add')
                advanced_url = admin_reverse('cms_pagetype_advanced', args=(self.page.pk,))
                page_settings_url = admin_reverse('cms_pagetype_change', args=(self.page.pk,))
                duplicate_page_url = admin_reverse('cms_pagetype_duplicate', args=[self.page.pk])
            else:
                add_page_url = admin_reverse('cms_page_add')
                advanced_url = admin_reverse('cms_page_advanced', args=(self.page.pk,))
                page_settings_url = admin_reverse('cms_page_change', args=(self.page.pk,))
                duplicate_page_url = admin_reverse('cms_page_duplicate', args=[self.page.pk])

            can_add_root_page = page_permissions.user_can_add_page(
                user=self.request.user,
                site=self.current_site,
            )

            if self.page.parent_page:
                new_page_params['parent_node'] = self.page.parent_page.node_id
                can_add_sibling_page = page_permissions.user_can_add_subpage(
                    user=self.request.user,
                    target=self.page.parent_page,
                )
            else:
                can_add_sibling_page = can_add_root_page

            can_add_sub_page = page_permissions.user_can_add_subpage(
                user=self.request.user,
                target=self.page,
            )

            # page operations menu
            add_page_menu = current_page_menu.get_or_create_menu(
                PAGE_MENU_ADD_IDENTIFIER,
                _('Create Page'),
            )

            add_page_menu_modal_items = (
                (_('New Page'), new_page_params, can_add_sibling_page),
                (_('New Sub Page'), new_sub_page_params, can_add_sub_page),
            )

            for title, params, has_perm in add_page_menu_modal_items:
                params.update(language=self.toolbar.request_language)
                add_page_menu.add_modal_item(
                    title,
                    url=add_url_parameters(add_page_url, params),
                    disabled=not has_perm,
                )

            add_page_menu.add_modal_item(
                _('Duplicate this Page'),
                url=add_url_parameters(
                    duplicate_page_url,
                    {'language': self.toolbar.request_language}
                ),
                disabled=not can_add_sibling_page,
            )

            # first break
            current_page_menu.add_break(PAGE_MENU_FIRST_BREAK)

            # page edit
            page_edit_url = '?%s' % get_cms_setting('CMS_TOOLBAR_URL__EDIT_ON')
            current_page_menu.add_link_item(
                _('Edit this Page'),
                disabled=edit_mode,
                url=page_edit_url
            )

            # page settings
            page_settings_url = add_url_parameters(
                page_settings_url,
                language=self.toolbar.request_language
            )
            settings_disabled = not edit_mode or not can_change
            current_page_menu.add_modal_item(
                _('Page settings'),
                url=page_settings_url,
                disabled=settings_disabled,
                on_close=refresh
            )

            # advanced settings
            advanced_url = add_url_parameters(
                advanced_url,
                language=self.toolbar.request_language
            )
            can_change_advanced = self.page.has_advanced_settings_permission(self.request.user)
            advanced_disabled = not edit_mode or not can_change_advanced
            current_page_menu.add_modal_item(
                _('Advanced settings'),
                url=advanced_url,
                disabled=advanced_disabled
            )

            # templates menu
            if edit_mode:
                if self.page.is_page_type:
                    action = admin_reverse('cms_pagetype_change_template', args=(self.page.pk,))
                else:
                    action = admin_reverse('cms_page_change_template', args=(self.page.pk,))

                if can_change_advanced:
                    templates_menu = current_page_menu.get_or_create_menu(
                        'templates',
                        _('Templates'),
                        disabled=not can_change,
                    )

                    for path, name in get_cms_setting('TEMPLATES'):
                        active = self.page.template == path
                        if path == TEMPLATE_INHERITANCE_MAGIC:
                            templates_menu.add_break(TEMPLATE_MENU_BREAK)
                        templates_menu.add_ajax_item(
                            name,
                            action=action,
                            data={'template': path},
                            active=active,
                            on_success=refresh
                        )

            # page type
            if not self.page.is_page_type:
                page_type_url = admin_reverse('cms_pagetype_add')
                page_type_url = add_url_parameters(
                    page_type_url,
                    source=self.page.pk,
                    language=self.toolbar.request_language
                )
                page_type_disabled = not edit_mode or not can_add_root_page
                current_page_menu.add_modal_item(
                    _('Save as Page Type'),
                    page_type_url,
                    disabled=page_type_disabled
                )

                # second break
                current_page_menu.add_break(PAGE_MENU_SECOND_BREAK)

            # permissions
            if self.permissions_activated:
                permissions_url = admin_reverse('cms_page_permissions', args=(self.page.pk,))
                permission_disabled = not edit_mode

                if not permission_disabled:
                    permission_disabled = not \
                            page_permissions.user_can_change_page_permissions(
                                user=self.request.user,
                                page=self.page,
                            )
                current_page_menu.add_modal_item(
                    _('Permissions'),
                    url=permissions_url,
                    disabled=permission_disabled
                )

            if not self.page.is_page_type:
                # dates settings
                dates_url = admin_reverse('cms_page_dates', args=(self.page.pk,))
                current_page_menu.add_modal_item(
                    _('Publishing dates'),
                    url=dates_url,
                    disabled=(not edit_mode or not can_change),
                )

                # third break
                current_page_menu.add_break(PAGE_MENU_THIRD_BREAK)

                # navigation toggle
                nav_title = _('Hide in navigation') if self.page.in_navigation \
                    else _('Display in navigation')
                nav_action = admin_reverse(
                    'cms_page_change_innavigation',
                    args=(self.page.pk,)
                )
                current_page_menu.add_ajax_item(
                    nav_title,
                    action=nav_action,
                    disabled=(not edit_mode or not can_change),
                    on_success=refresh,
                )

            # publisher
            if self.title and not self.page.is_page_type:
                if self.title.published:
                    publish_title = _('Unpublish page')
                    publish_url = admin_reverse(
                        'cms_page_unpublish',
                        args=(self.page.pk, self.current_lang)
                    )
                else:
                    publish_title = _('Publish page')
                    publish_url = admin_reverse(
                        'cms_page_publish_page',
                        args=(self.page.pk, self.current_lang)
                    )

                user_can_publish = user_can_publish_page(self.request.user, page=self.page)
                current_page_menu.add_ajax_item(
                    publish_title,
                    action=publish_url,
                    disabled=not edit_mode or not user_can_publish,
                    on_success=refresh,
                )

            if self.current_lang and not self.page.is_page_type:
                # revert to live
                current_page_menu.add_break(PAGE_MENU_FOURTH_BREAK)
                revert_action = admin_reverse(
                    'cms_page_revert_to_live',
                    args=(self.page.pk, self.current_lang)
                )
                revert_question = _('Are you sure you want to revert to live?')
                # Only show this action if the page has pending changes and a public version
                is_enabled = (
                    edit_mode
                    and can_change
                    and self.page.is_dirty(self.current_lang)
                    and self.page.publisher_public
                )
                current_page_menu.add_ajax_item(
                    _('Revert to live'),
                    action=revert_action,
                    question=revert_question,
                    disabled=not is_enabled,
                    on_success=refresh,
                    extra_classes=('cms-toolbar-revert',),
                )

                # last break
                current_page_menu.add_break(PAGE_MENU_LAST_BREAK)

            # delete
            if self.page.is_page_type:
                delete_url = admin_reverse('cms_pagetype_delete', args=(self.page.pk,))
            else:
                delete_url = admin_reverse('cms_page_delete', args=(self.page.pk,))
            delete_disabled = not edit_mode or not user_can_delete_page(
                self.request.user,
                page=self.page
            )
            on_delete_redirect_url = self.get_on_delete_redirect_url()
            current_page_menu.add_modal_item(
                _('Delete page'),
                url=delete_url,
                on_close=on_delete_redirect_url,
                disabled=delete_disabled
            )


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
