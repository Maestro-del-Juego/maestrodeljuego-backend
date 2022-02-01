from datetime import datetime, date
from celery import Celery
from django.core.mail import send_mail
from games import settings
from games.celery import app

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

@app.task
def feedback_email(subject, message, email_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=email_list
    )