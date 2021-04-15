from django.test import TestCase
from django.utils import timezone
from .models import PullRequest, is_there_migrations_to_make
from django.conf import settings


class MigrationsTests(TestCase):
    def test_no_migrations_to_make(self):

        apps = settings.INSTALLED_APPS
        apps_exception = [
            '_mono.apps.MyAdminConfig',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admindocs',
            'rest_framework',
            'rest_framework.authtoken',
            'social_django',
        ]
        for app in apps_exception:
            apps.remove(app)
        for app in apps:
            self.assertFalse(is_there_migrations_to_make(app), "You have migrations to make. Run 'manage.py makemigrations'.")


class PullRequestModelTests(TestCase):

    def setUp(self):
        self.pull_request = PullRequest.objects.create(
            number=1,
            merged_at=timezone.now()
        )

    def test_pull_request_creation(self):
        self.assertIsNotNone(self.pull_request.pk)

    def test_deploy(self):
        self.pull_request.deploy()
