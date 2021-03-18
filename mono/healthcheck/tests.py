from django.test import TestCase
from .models import PullRequest, is_database_synchronized, is_there_migrations_to_make

# Create your tests here.

class MigrationsTests(TestCase):
    def test_no_migrations_to_make(self):
        self.assertFalse(is_there_migrations_to_make(), "You have migrations to make. Run 'manage.py makemigrations'.")

    def test_no_migrations_to_apply(self):
        self.assertTrue(is_database_synchronized(), "You have pending migrations to apply. Run 'manage.py migrate'.")

class PullRequestModelTests(TestCase):

    def setUp(self):
        self.pull_request = PullRequest.objects.create(number=1)

    def test_pull_request_creation(self):
        self.assertIsNotNone(self.pull_request.pk)

    def test_deploy(self):
        self.pull_request.deploy()
        pass