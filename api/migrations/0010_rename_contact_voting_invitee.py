# Generated by Django 4.0.1 on 2022-01-20 01:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_contact_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='voting',
            old_name='contact',
            new_name='invitee',
        ),
    ]
