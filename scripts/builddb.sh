#!/bin/bash

rm project.db
rm users.db
python manage.py migrate --database default 
python manage.py migrate --database auth_db 
python manage.py createsuperuser --database auth_db
