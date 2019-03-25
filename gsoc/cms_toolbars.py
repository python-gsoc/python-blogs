from cms.cms_toolbars import BasicToolbar

from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from cms.utils.conf import get_cms_setting
from cms.utils.urlutils import admin_reverse


# # Identifiers for search
ADMIN_MENU_IDENTIFIER = 'admin-menu'
ADMINISTRATION_BREAK = 'Administration Break'
USER_SETTINGS_BREAK = 'User Settings Break'
TOOLBAR_DISABLE_BREAK = 'Toolbar disable Break'
SHORTCUTS_BREAK = 'Shortcuts Break'
CLIPBOARD_BREAK = 'Clipboard Break'

def add_admin_menu(self):
    if not self._admin_menu:
        self._admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, self.current_site.name)
        # Users button
        self.add_users_button(self._admin_menu)

        # sites menu
        sites_queryset = Site.objects.order_by('name')

        if len(sites_queryset) > 1:
            sites_menu = self._admin_menu.get_or_create_menu('sites', _('Sites'))
            sites_menu.add_sideframe_item(_('Admin Sites'), url=admin_reverse('sites_site_changelist'))
            sites_menu.add_break(ADMIN_SITES_BREAK)
            for site in sites_queryset:
                sites_menu.add_link_item(site.name, url='http://%s' % site.domain,
                                            active=site.pk == self.current_site.pk)

        # admin
        self._admin_menu.add_sideframe_item(_('Administration'), url=admin_reverse('index'))

        # scheduler
        self._admin_menu.add_sideframe_item(_('Schedulers'), url=admin_reverse('gsoc_scheduler_changelist'))
        self._admin_menu.add_break(ADMINISTRATION_BREAK)

        # cms users settings
        self._admin_menu.add_sideframe_item(_('User settings'), url=admin_reverse('cms_usersettings_change'))
        self._admin_menu.add_break(USER_SETTINGS_BREAK)

        # clipboard
        if self.toolbar.edit_mode_active:
            # True if the clipboard exists and there's plugins in it.
            clipboard_is_bound = self.toolbar.clipboard_plugin

            self._admin_menu.add_link_item(_('Clipboard...'), url='#',
                    extra_classes=['cms-clipboard-trigger'],
                    disabled=not clipboard_is_bound)
            self._admin_menu.add_link_item(_('Clear clipboard'), url='#',
                    extra_classes=['cms-clipboard-empty'],
                    disabled=not clipboard_is_bound)
            self._admin_menu.add_break(CLIPBOARD_BREAK)

        # Disable toolbar
        self._admin_menu.add_link_item(_('Disable toolbar'), url='?%s' % get_cms_setting('CMS_TOOLBAR_URL__DISABLE'))
        self._admin_menu.add_break(TOOLBAR_DISABLE_BREAK)
        self._admin_menu.add_link_item(_('Shortcuts...'), url='#',
                extra_classes=('cms-show-shortcuts',))
        self._admin_menu.add_break(SHORTCUTS_BREAK)

        # logout
        self.add_logout_button(self._admin_menu)

BasicToolbar.add_admin_menu = add_admin_menu