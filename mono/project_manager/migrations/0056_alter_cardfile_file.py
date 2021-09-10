# Generated by Django 3.2.7 on 2021-09-10 20:01

from django.db import migrations, models
import project_manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0055_alter_cardfile_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardfile',
            name='file',
            field=models.FileField(default=0, max_length=1000, upload_to=project_manager.models.CardFile._card_directory_path),
            preserve_default=False,
        ),
    ]
