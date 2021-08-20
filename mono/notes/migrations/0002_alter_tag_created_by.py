# Generated by Django 3.2.4 on 2021-08-18 12:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='created_by',
            field=models.ForeignKey(help_text='Identifies who created the tag.', on_delete=django.db.models.deletion.CASCADE, related_name='note_tags', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
    ]