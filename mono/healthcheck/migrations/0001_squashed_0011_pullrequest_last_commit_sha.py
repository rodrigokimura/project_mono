# Generated by Django 3.2.11 on 2022-01-25 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('healthcheck', '0001_initial'), ('healthcheck', '0002_auto_20210318_1115'), ('healthcheck', '0003_auto_20210318_1404'), ('healthcheck', '0004_auto_20210318_1442'), ('healthcheck', '0005_auto_20210318_1505'), ('healthcheck', '0006_auto_20210318_1508'), ('healthcheck', '0007_pullrequest_migrations'), ('healthcheck', '0008_auto_20210318_1554'), ('healthcheck', '0009_alter_pullrequest_id'), ('healthcheck', '0010_alter_pullrequest_options'), ('healthcheck', '0011_pullrequest_last_commit_sha')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(help_text='GitHub unique identifier.', unique=True)),
                ('author', models.CharField(help_text='Login username that triggered the pull request.', max_length=100)),
                ('commits', models.IntegerField(default=0)),
                ('additions', models.IntegerField(default=0)),
                ('deletions', models.IntegerField(default=0)),
                ('changed_files', models.IntegerField(default=0)),
                ('merged_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                ('pulled_at', models.DateTimeField(blank=True, default=None, help_text='Set when pull method runs.', null=True)),
                ('deployed_at', models.DateTimeField(blank=True, default=None, help_text='Set when deploy method runs.', null=True)),
                ('migrations', models.IntegerField(blank=True, default=None, null=True)),
                ('last_commit_sha', models.CharField(blank=True, help_text='SHA of the last commit.', max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Pull Request',
                'verbose_name_plural': 'Pull Requests',
                'get_latest_by': 'number',
            },
        ),
    ]