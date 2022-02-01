web: gunicorn games.wsgi
release: python manage.py migrate
worker: celery worker --app=games worker --loglevel=INFO