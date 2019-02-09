python manage.py migrate --database default 
python manage.py migrate --database auth_db auth
python manage.py migrate --database auth_db admin
python manage.py migrate --database auth_db sessions
python manage.py createsuperuser --database auth_db
