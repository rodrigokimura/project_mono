# Generated by Django 3.2.7 on 2021-10-03 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0049_auto_20211003_0100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='closing_date',
            new_name='settlement_date',
        ),
    ]
