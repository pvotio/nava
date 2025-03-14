#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py collectstatic --noinput

if [ "$DJANGO_ENV" = "production" ]; then
    echo "PRODUCTION ENV"
    gunicorn config.wsgi:application --bind 0.0.0.0:8000
else
    echo "DEBUG ENV"
    python manage.py runserver 0.0.0.0:8000
fi

exec "$@"