# Generated by Django 3.2.4 on 2021-08-05 18:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_manager', '0016_auto_20210805_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='color',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='project_manager.theme'),
        ),
    ]