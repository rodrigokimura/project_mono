# Generated by Django 3.2.7 on 2021-10-04 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0002_alter_event_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='traceback',
            name='code_text',
            field=models.JSONField(),
        ),
    ]
