# Generated by Django 3.2.13 on 2022-05-13 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checklists', '0005_auto_20220513_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='reminded',
            field=models.BooleanField(default=False),
        ),
    ]