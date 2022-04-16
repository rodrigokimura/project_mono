# Generated by Django 3.2.13 on 2022-04-16 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthcheck', '0001_squashed_0011_pullrequest_last_commit_sha'),
    ]

    operations = [
        migrations.CreateModel(
            name='PytestReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pytest_version', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PytestTestResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_id', models.CharField(help_text='Test unique identifier.', max_length=2000)),
                ('duration', models.FloatField(help_text='Test duration in seconds.')),
                ('outcome', models.CharField(choices=[('passed', 'Passed'), ('failed', 'Failed')], help_text='Test outcome.', max_length=6)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='healthcheck.pytestreport')),
            ],
        ),
    ]