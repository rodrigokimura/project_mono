# Generated by Django 3.2.7 on 2021-10-05 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0003_alter_traceback_code_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='traceback',
            options={'ordering': ['-order']},
        ),
    ]