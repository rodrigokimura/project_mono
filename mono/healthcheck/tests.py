import hmac
import json
from datetime import datetime
from hashlib import sha1

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.utils.encoding import force_bytes

from .models import PullRequest, is_there_migrations_to_make
from .tasks import deploy_app

User = get_user_model()


class AdminTests(TestCase):
    fixtures = ['icon']


class MigrationsTests(TestCase):
    def test_no_migrations_to_make(self):

        apps = settings.INSTALLED_APPS
        apps_exception = [
            '__mono.apps.MyAdminConfig',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admindocs',
            'rest_framework',
            'rest_framework.authtoken',
            'social_django',
            'background_task',
            'django.forms',
        ]
        for app in apps_exception:
            apps.remove(app)
        for app in apps:
            self.assertFalse(
                is_there_migrations_to_make(app_label=app, silent=True),
                "You have migrations to make. Run 'manage.py makemigrations'."
            )


class PullRequestModelTests(TestCase):

    def setUp(self):
        self.pull_request = PullRequest.objects.create(
            number=1,
            merged_at=timezone.now()
        )

    def test_pull_request_creation(self):
        self.assertIsNotNone(self.pull_request.pk)


class GithubWebhookView(TestCase):

    def setUp(self) -> None:
        self.valid_payload = {
            'pull_request': {
                'number': '1',
                'base': {'ref': 'master'},
                'merged': True,
                'user': {'login': 'rodrigokimura'},
                'commits': '2',
                'additions': '2',
                'deletions': '2',
                'changed_files': '2',
                'merged_at': datetime.strftime(timezone.now(), '%Y-%m-%dT%H:%M:%SZ'),
            },
            'action': 'closed'
        }

    def test_ping(self):
        c = Client()
        payload = {'test': True}
        payload_bytes = json.dumps(payload).encode('utf-8')
        mac = hmac.new(force_bytes(settings.GITHUB_SECRET), msg=force_bytes(payload_bytes), digestmod=sha1)
        headers = {
            'HTTP_X-GitHub-Event': 'ping',
            'HTTP_X-Hub-Signature': f'sha1={mac.hexdigest()}',
        }
        response = c.post(
            '/hc/update_app/',
            data=payload,
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, 200)

    def test_valid_signature(self):
        c = Client()
        payload_bytes = json.dumps(self.valid_payload).encode('utf-8')
        mac = hmac.new(force_bytes(settings.GITHUB_SECRET), msg=force_bytes(payload_bytes), digestmod=sha1)
        headers = {
            'HTTP_X-GitHub-Event': 'pull_request',
            'HTTP_X-Hub-Signature': f'sha1={mac.hexdigest()}',
        }
        response = c.post(
            '/hc/update_app/',
            data=self.valid_payload,
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_signature(self):
        c = Client()
        payload = {'test': True}
        headers = {
            'HTTP_X-GitHub-Event': 'ping',
            'HTTP_X-Hub-Signature': 'sha1=invalid',
        }
        response = c.post(
            '/hc/update_app/',
            data=payload,
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_signature_algorithm(self):
        c = Client()
        payload = {'test': True}
        headers = {
            'HTTP_X-GitHub-Event': 'ping',
            'HTTP_X-Hub-Signature': 'sha2=invalid',
        }
        response = c.post(
            '/hc/update_app/',
            data=payload,
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_event(self):
        c = Client()
        payload = {'test': True}
        payload_bytes = json.dumps(payload).encode('utf-8')
        mac = hmac.new(force_bytes(settings.GITHUB_SECRET), msg=force_bytes(payload_bytes), digestmod=sha1)
        headers = {
            'HTTP_X-GitHub-Event': 'invalid_event',
            'HTTP_X-Hub-Signature': f'sha1={mac.hexdigest()}',
        }
        response = c.post(
            '/hc/update_app/',
            data=payload,
            content_type='application/json',
            **headers
        )
        self.assertEqual(response.status_code, 200)


class HealthCheckView(TestCase):

    def test_get(self):
        PullRequest.objects.create(
            number=1,
            merged_at=timezone.now(),
            deployed_at=timezone.now(),
        )
        c = Client()
        response = c.get('/hc/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'build_number')


class DeployView(TestCase):

    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create(username="notsuperuser", email="test@test.com")
        self.superuser = User.objects.create(username="superuser", email="test@test.com")
        self.superuser.is_superuser = True
        self.superuser.save()
        self.pull_request = PullRequest.objects.create(
            number=1,
            merged_at=timezone.now()
        )

    def test_invalid_user(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/hc/deploy/')
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get('/hc/deploy/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.post('/hc/deploy/', {'pk': 1})
        self.assertEqual(response.status_code, 200)


class ModelTests(TestCase):

    def setUp(self) -> None:
        self.pull_request: PullRequest = PullRequest.objects.create(
            number=1,
            merged_at=timezone.now()
        )

    def test_merged(self):
        self.assertTrue(self.pull_request.merged)

    def test_pull(self):
        self.pull_request.pull()
        self.assertTrue(self.pull_request.pulled)


class TaskTests(TestCase):

    def setUp(self) -> None:
        self.pull_request: PullRequest = PullRequest.objects.create(
            number=1,
            merged_at=timezone.now()
        )

    def test_task(self):
        deploy_app.now(self.pull_request.number)
