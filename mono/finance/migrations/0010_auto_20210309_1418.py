# Generated by Django 3.1.7 on 2021-03-09 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0009_auto_20210308_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='belongs_to',
        ),
        migrations.AddField(
            model_name='account',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_accountset', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='account',
            name='owned_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='owned_accountset', to='auth.user'),
            preserve_default=False,
        ),
    ]
