# Generated by Django 4.0.1 on 2022-01-20 22:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_alter_gamenight_games'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='game1_rating',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='game2_rating',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='game3_rating',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='game4_rating',
        ),
        migrations.RemoveField(
            model_name='feedback',
            name='game5_rating',
        ),
        migrations.CreateModel(
            name='GameFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('feedback', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='api.feedback')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game', to='api.game')),
            ],
        ),
        migrations.AddConstraint(
            model_name='gamefeedback',
            constraint=models.UniqueConstraint(fields=('feedback', 'game'), name='unique-game-feedback'),
        ),
    ]
