import hmac
import json
from datetime import datetime
from hashlib import sha1

from __mono.decorators import ignore_warnings
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.utils.encoding import force_bytes
from finance.models import Icon

from .models import PullRequest
from .tasks import deploy_app

User = get_user_model()


class MigrationsCheck(TestCase):
    def setUp(self):
        from django.utils import translation

        self.saved_locale = translation.get_language()
        translation.deactivate_all()

    def tearDown(self):
        if self.saved_locale is not None:
            from django.utils import translation

            translation.activate(self.saved_locale)

    def test_missing_migrations(self):
        from django.apps.registry import apps
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        from django.db.migrations.autodetector import MigrationAutodetector
        from django.db.migrations.state import ProjectState

        autodetector = MigrationAutodetector(
            executor.loader.project_state(),
            ProjectState.from_apps(apps),
        )
        changes = autodetector.changes(graph=executor.loader.graph)
        third_party_apps = [
            "background_task",
        ]
        for app in third_party_apps:
            if app in changes:
                del changes[app]  # pragma: no cover
        self.assertEqual({}, changes)


class PullRequestModelTests(TestCase):
    def setUp(self):
        self.pull_request = PullRequest.objects.create(
            number=1, merged_at=timezone.now()
        )

    def test_pull_request_creation(self):
        self.assertIsNotNone(self.pull_request.pk)


class GithubWebhookView(TestCase):
    def setUp(self) -> None:
        self.valid_payload = {
            "pull_request": {
                "number": "1",
                "base": {
                    "ref": "master",
                    "sha": "a" * 40,
                },
                "merged": True,
                "user": {"login": "rodrigokimura"},
                "commits": "2",
                "additions": "2",
                "deletions": "2",
                "changed_files": "2",
                "merged_at": datetime.strftime(
                    timezone.now(), "%Y-%m-%dT%H:%M:%SZ"
                ),
            },
            "action": "closed",
        }

    def test_ping(self):
        c = Client()
        payload = {"test": True}
        payload_bytes = json.dumps(payload).encode("utf-8")
        mac = hmac.new(
            force_bytes(settings.GITHUB_SECRET),
            msg=force_bytes(payload_bytes),
            digestmod=sha1,
        )
        headers = {
            "HTTP_X-GitHub-Event": "ping",
            "HTTP_X-Hub-Signature": f"sha1={mac.hexdigest()}",
        }
        response = c.post(
            "/hc/update_app/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    def test_valid_signature(self):
        c = Client()
        payload_bytes = json.dumps(self.valid_payload).encode("utf-8")
        mac = hmac.new(
            force_bytes(settings.GITHUB_SECRET),
            msg=force_bytes(payload_bytes),
            digestmod=sha1,
        )
        headers = {
            "HTTP_X-GitHub-Event": "pull_request",
            "HTTP_X-Hub-Signature": f"sha1={mac.hexdigest()}",
        }
        response = c.post(
            "/hc/update_app/",
            data=self.valid_payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_invalid_signature(self):
        c = Client()
        payload = {"test": True}
        headers = {
            "HTTP_X-GitHub-Event": "ping",
            "HTTP_X-Hub-Signature": "sha1=invalid",
        }
        response = c.post(
            "/hc/update_app/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    @ignore_warnings
    def test_invalid_signature_algorithm(self):
        c = Client()
        payload = {"test": True}
        headers = {
            "HTTP_X-GitHub-Event": "ping",
            "HTTP_X-Hub-Signature": "sha2=invalid",
        }
        response = c.post(
            "/hc/update_app/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 403)

    @ignore_warnings
    def test_invalid_event(self):
        c = Client()
        payload = {"test": True}
        payload_bytes = json.dumps(payload).encode("utf-8")
        mac = hmac.new(
            force_bytes(settings.GITHUB_SECRET),
            msg=force_bytes(payload_bytes),
            digestmod=sha1,
        )
        headers = {
            "HTTP_X-GitHub-Event": "invalid_event",
            "HTTP_X-Hub-Signature": f"sha1={mac.hexdigest()}",
        }
        response = c.post(
            "/hc/update_app/",
            data=payload,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 403)


class HealthCheckView(TestCase):
    def test_get(self):
        PullRequest.objects.create(
            number=1,
            merged_at=timezone.now(),
            deployed_at=timezone.now(),
        )
        c = Client()
        response = c.get("/hc/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "build_number")


class HomePageView(TestCase):
    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(
            username="notsuperuser", email="test@test.com"
        )
        self.superuser = User.objects.create(
            username="superuser", email="test@test.com"
        )
        self.superuser.is_superuser = True
        self.superuser.save()

    @ignore_warnings
    def test_get(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get("/hc/home/")
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_get_forbidden(self):
        c = Client()
        c.force_login(self.user)
        response = c.get("/hc/home/")
        self.assertEqual(response.status_code, 403)


class CommitsByDateView(TestCase):
    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(
            username="notsuperuser", email="test@test.com"
        )
        self.superuser = User.objects.create(
            username="superuser", email="test@test.com"
        )
        self.superuser.is_superuser = True
        self.superuser.save()

    @ignore_warnings
    def test_get(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get("/hc/api/commits/by-date/", {"date": "2020-01-01"})
        self.assertEqual(response.status_code, 200)

    @ignore_warnings
    def test_get_bad_request(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get("/hc/api/commits/by-date/")
        self.assertEqual(response.status_code, 400)

    @ignore_warnings
    def test_get_forbidden(self):
        c = Client()
        c.force_login(self.user)
        response = c.get("/hc/api/commits/by-date/", {"date": "2020-01-01"})
        self.assertEqual(response.status_code, 403)


class DeployView(TestCase):
    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(
            username="notsuperuser", email="test@test.com"
        )
        self.superuser = User.objects.create(
            username="superuser", email="test@test.com"
        )
        self.superuser.is_superuser = True
        self.superuser.save()
        self.pull_request = PullRequest.objects.create(
            number=1, merged_at=timezone.now()
        )

    @ignore_warnings
    def test_invalid_user(self):
        c = Client()
        c.force_login(self.user)
        response = c.get("/hc/deploy/")
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get("/hc/deploy/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.post("/hc/deploy/", {"pk": 1})
        self.assertEqual(response.status_code, 200)


class ModelTests(TestCase):
    def setUp(self) -> None:
        self.pull_request: PullRequest = PullRequest.objects.create(
            number=1, merged_at=timezone.now()
        )

    def test_merged(self):
        self.assertTrue(self.pull_request.merged)

    def test_pull(self):
        self.pull_request.pull()
        self.assertTrue(self.pull_request.pulled)


class TaskTests(TestCase):
    def setUp(self) -> None:
        self.pull_request: PullRequest = PullRequest.objects.create(
            number=1, merged_at=timezone.now()
        )

    def test_task(self):
        deploy_app.now(self.pull_request.number)
