# Generated by Django 3.2.14 on 2022-07-22 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_squashed_0009_alter_plan_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='telegram_chat_id',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
    ]
