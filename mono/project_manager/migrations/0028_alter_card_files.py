# Generated by Django 3.2.4 on 2021-08-11 17:50

from django.db import migrations, models
import project_manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0027_alter_invite_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to=project_manager.models.card_directory_path),
        ),
    ]
