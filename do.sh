python3.6 manage.py migrate --database default 
python3.6 manage.py migrate --database auth_db auth
python3.6 manage.py migrate --database auth_db admin
python3.6 manage.py migrate --database auth_db sessions
python3.6 manage.py createsuperuser --database auth_db
