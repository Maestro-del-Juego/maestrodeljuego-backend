# Generated by Django 4.0.1 on 2022-01-21 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_voting_game'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='voting',
            name='unique-vote',
        ),
        migrations.AddConstraint(
            model_name='voting',
            constraint=models.UniqueConstraint(fields=('gamenight', 'invitee', 'game'), name='unique-vote'),
        ),
    ]
