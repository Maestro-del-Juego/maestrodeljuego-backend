web: gunicorn games.wsgi
release: python manage.py migrate
worker: celery worker -A games worker --loglevel=INFO