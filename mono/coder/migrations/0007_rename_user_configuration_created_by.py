# Generated by Django 3.2.12 on 2022-02-18 01:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coder', '0006_alter_snippet_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='configuration',
            old_name='user',
            new_name='created_by',
        ),
    ]
