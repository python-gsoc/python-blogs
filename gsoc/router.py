from django.conf import settings
from cms.models import PageUser


class DatabaseAppsRouter(object):
    """
    A router to control all database operations on models for different
    databases.

    In case an app is not set in settings.DATABASE_APPS_MAPPING, the router
    will fallback to the `default` database.

    Settings example:

    DATABASE_APPS_MAPPING = {'app1': 'db1', 'app2': 'db2'}
    """

    def db_for_read(self, model, **hints):
        """Point all read operations to the specific database."""
        if model == PageUser:
            return 'auth_db'
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Point all write operations to the specific database."""
        if model == PageUser:
            return 'auth_db'
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
#        """Allow any relation."""
#        db_obj1 = settings.DATABASE_APPS_MAPPING.get(obj1._meta.app_label)
#        db_obj2 = settings.DATABASE_APPS_MAPPING.get(obj2._meta.app_label)
#        if db_obj1 and db_obj2:
#            if db_obj1 == db_obj2:
#                return True
#            else:
#                return False
        return True

    def allow_syncdb(self, db, model):
        """Make sure that apps only appear in the related database."""
        if model == PageUser:
            return 'auth_db'
        elif db in list(settings.DATABASE_APPS_MAPPING.values()):
            return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label) == db
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure that apps only appear in the related database."""
        if app_label == 'cms' and model_name == 'pageuser':
            return 'auth_db' == db
        elif app_label == 'contenttypes':
            return True
        elif db in list(settings.DATABASE_APPS_MAPPING.values()):
            return settings.DATABASE_APPS_MAPPING.get(app_label) == db
        elif app_label in settings.DATABASE_APPS_MAPPING:
            return False
        return None
