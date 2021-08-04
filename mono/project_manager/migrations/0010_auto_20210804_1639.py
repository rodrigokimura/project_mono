# Generated by Django 3.2.4 on 2021-08-04 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project_manager', '0009_alter_timeentry_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='card',
            name='started_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='started_cards', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='card',
            name='status',
            field=models.CharField(choices=[('NS', 'Not started'), ('IP', 'In progress'), ('C', 'Completed')], default='NS', max_length=2, verbose_name='status'),
        ),
    ]
