# Generated by Django 3.2.7 on 2021-10-12 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0057_auto_20211012_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='time_entries_feature',
            field=models.BooleanField(default=True, help_text='Enables users to track time spent on cards'),
        ),
    ]
