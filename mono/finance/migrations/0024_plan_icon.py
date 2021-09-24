# Generated by Django 3.1.7 on 2021-03-25 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0023_auto_20210325_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='icon',
            field=models.ForeignKey(blank=True, default=None, help_text='Icon rendered in the template', null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.icon'),
        ),
    ]
