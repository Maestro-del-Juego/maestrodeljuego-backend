# Generated by Django 4.0.1 on 2022-01-25 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_rsvp_unique-rsvp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalfeedback',
            name='gamenight',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='generalfeedback', to='api.gamenight'),
        ),
    ]