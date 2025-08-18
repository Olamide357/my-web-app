release: python manage.py migrate --noinput
web: gunicorn project.wsgi:application --bind 0.0.0.0:$PORT