# Generated by Django 3.1.7 on 2021-03-30 19:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0031_auto_20210329_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetconfiguration',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='created_by',
            field=models.ForeignKey(help_text='Identifies who created the transaction.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
    ]
