web: gunicorn games.wsgi
release: python manage.py migrate
worker: celery --app=games worker --loglevel=INFO