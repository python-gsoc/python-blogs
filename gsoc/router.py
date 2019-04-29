class DatabaseAppsRouter():

    """
    def db_for_read(self, model, **hints):
        if model == PageUser:
            return 'auth_db'
        if model == PageUserGroup:
            return 'default'
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        if model == PageUser:
            return 'auth_db'
        if model == PageUserGroup:
            return 'default'
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
#        db_obj1 = settings.DATABASE_APPS_MAPPING.get(obj1._meta.app_label)
#        db_obj2 = settings.DATABASE_APPS_MAPPING.get(obj2._meta.app_label)
#        if db_obj1 and db_obj2:
#            if db_obj1 == db_obj2:
#                return True
#            else:
#                return False
        return True

    def allow_syncdb(self, db, model):
        if model == PageUser:
            return 'auth_db'
        elif db in list(settings.DATABASE_APPS_MAPPING.values()):
            return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label) == db
        elif model._meta.app_label in settings.DATABASE_APPS_MAPPING:
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'cms' and model_name == 'pageuser':
            return 'auth_db' == db
        elif app_label == 'contenttypes':
            return True
        elif app_label == 'auth' and model_name == 'permission':
            return 'default'
        elif db in list(settings.DATABASE_APPS_MAPPING.values()):
            return settings.DATABASE_APPS_MAPPING.get(app_label) == db
        elif app_label in settings.DATABASE_APPS_MAPPING:
            return False
        return None
"""
