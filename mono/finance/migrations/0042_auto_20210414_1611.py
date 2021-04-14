# Generated by Django 3.2 on 2021-04-14 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0041_auto_20210413_1749'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='all_accounts',
            field=models.BooleanField(default=False, verbose_name='all accounts'),
        ),
        migrations.AddField(
            model_name='budget',
            name='all_categories',
            field=models.BooleanField(default=False, verbose_name='all categories'),
        ),
        migrations.AddField(
            model_name='budgetconfiguration',
            name='all_accounts',
            field=models.BooleanField(default=False, verbose_name='all accounts'),
        ),
        migrations.AddField(
            model_name='budgetconfiguration',
            name='all_categories',
            field=models.BooleanField(default=False, verbose_name='all categories'),
        ),
    ]
