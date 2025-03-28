#!/usr/bin/env bash
# This script is used to build the LibrarySystem project.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
