# Generated by Django 4.1.4 on 2022-12-15 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("typer", "0002_rename_miliseconds_keypress_milliseconds"),
    ]

    operations = [
        migrations.AddField(
            model_name="record",
            name="accuracy",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="record",
            name="chars_per_minute",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
