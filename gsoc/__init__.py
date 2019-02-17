from django.db.backends.signals import connection_created

#disable foreign_keys so that everything works with multi-database
def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = "0";')

connection_created.connect(activate_foreign_keys)