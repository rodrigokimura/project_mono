# Generated by Django 3.2.4 on 2021-09-07 14:04

import project_manager.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0052_board_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='background_image',
            field=models.ImageField(blank=True, null=True, upload_to=project_manager.models.Board._background_image_path),
        ),
    ]
