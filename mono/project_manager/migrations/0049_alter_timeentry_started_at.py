# Generated by Django 3.2.4 on 2021-08-26 13:59

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0048_alter_comment_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeentry',
            name='started_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
