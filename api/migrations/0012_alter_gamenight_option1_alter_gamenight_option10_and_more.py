# Generated by Django 4.0.1 on 2022-01-20 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_contact_unique-contact_feedback_unique-feedback_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamenight',
            name='option1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option1', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option10',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option10', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option2', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option3', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option4', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option5', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option6',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option6', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option7',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option7', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option8',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option8', to='api.game'),
        ),
        migrations.AlterField(
            model_name='gamenight',
            name='option9',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='option9', to='api.game'),
        ),
    ]
