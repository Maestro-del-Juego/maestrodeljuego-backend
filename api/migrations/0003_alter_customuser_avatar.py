# Generated by Django 4.0.1 on 2022-01-18 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_tag_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.URLField(blank=True, default=''),
        ),
    ]
