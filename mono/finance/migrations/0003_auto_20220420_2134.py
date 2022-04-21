# Generated by Django 3.2.13 on 2022-04-21 00:34

from django.db import migrations
from ..models import Icon


def create_default_icons(*args, **kwargs):
    Icon.create_defaults()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20220125_1646'),
    ]

    operations = [
        migrations.RunPython(create_default_icons)
    ]
