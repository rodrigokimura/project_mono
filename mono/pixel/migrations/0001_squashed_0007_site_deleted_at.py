# Generated by Django 3.2.11 on 2022-01-25 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    replaces = [('pixel', '0001_initial'), ('pixel', '0002_site_host'), ('pixel', '0003_auto_20210916_1852'), ('pixel', '0004_alter_ping_pageload_timestamp'), ('pixel', '0005_site_created_by'), ('pixel', '0006_site_created_at'), ('pixel', '0007_site_deleted_at')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('host', models.CharField(help_text='Host of the URL. Port or userinfo should be ommited. https://en.wikipedia.org/wiki/URL', max_length=1024, null=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
                ('created_at', models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=1024, null=True)),
                ('event', models.CharField(max_length=1024, null=True)),
                ('event_data', models.CharField(max_length=1024, null=True)),
                ('openpixel_js_version', models.CharField(max_length=1024, null=True)),
                ('document_location', models.CharField(max_length=1024, null=True)),
                ('referrer_location', models.CharField(max_length=1024, null=True)),
                ('timestamp', models.DateTimeField(null=True)),
                ('encoding', models.CharField(max_length=1024, null=True)),
                ('screen_resolution', models.CharField(max_length=50, null=True)),
                ('viewport', models.CharField(max_length=50, null=True)),
                ('document_title', models.CharField(max_length=1024, null=True)),
                ('browser_name', models.CharField(max_length=1024, null=True)),
                ('mobile_device', models.BooleanField(null=True)),
                ('user_agent', models.CharField(max_length=1024, null=True)),
                ('timezone_offset', models.IntegerField(null=True)),
                ('utm_source', models.CharField(max_length=1024, null=True)),
                ('utm_medium', models.CharField(max_length=1024, null=True)),
                ('utm_term', models.CharField(max_length=1024, null=True)),
                ('utm_content', models.CharField(max_length=1024, null=True)),
                ('utm_campaign', models.CharField(max_length=1024, null=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pixel.site')),
                ('duration', models.DurationField(null=True)),
                ('pageclose_timestamp', models.DateTimeField(null=True)),
                ('pageload_timestamp', models.DateTimeField(null=True)),
            ],
        ),
    ]