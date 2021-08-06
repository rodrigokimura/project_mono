# Generated by Django 3.2.4 on 2021-08-01 22:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_manager', '0002_auto_20210409_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='completed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='completed_cards', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='card',
            name='description',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='card',
            name='files',
            field=models.FileField(blank=True, null=True, upload_to=None),
        ),
    ]