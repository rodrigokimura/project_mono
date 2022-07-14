# Generated by Django 3.2.13 on 2022-07-04 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_manager', '0012_activity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'verbose_name': 'activity', 'verbose_name_plural': 'activities'},
        ),
        migrations.RemoveField(
            model_name='board',
            name='bucket_width',
        ),
        migrations.RemoveField(
            model_name='board',
            name='compact',
        ),
        migrations.RemoveField(
            model_name='board',
            name='dark',
        ),
        migrations.RemoveField(
            model_name='board',
            name='fullscreen',
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('compact', models.BooleanField(default=False)),
                ('dark', models.BooleanField(default=False)),
                ('bucket_width', models.IntegerField(default=300)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='project_manager_config', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'configuration',
                'verbose_name_plural': 'configurations',
            },
        ),
    ]