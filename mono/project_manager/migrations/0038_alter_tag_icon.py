# Generated by Django 3.2.4 on 2021-08-18 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0037_auto_20210818_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='icon',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project_manager.icon'),
        ),
    ]