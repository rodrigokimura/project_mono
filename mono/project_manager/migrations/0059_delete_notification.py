# Generated by Django 3.2.7 on 2021-11-04 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0058_board_time_entries_feature'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]