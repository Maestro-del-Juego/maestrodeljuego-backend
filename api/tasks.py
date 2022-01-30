from datetime import datetime, date
from celery import Celery
from django.core.mail import send_mail
from games import settings

app = Celery('games', broker='redis://localhost')

@app.task
def test_email(dt):
    message = f"The datetime is {dt}."
    email_list = ['jbandrew14@gmail.com']
    send_mail(
        subject='testing',
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email_list
    )