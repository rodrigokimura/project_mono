from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone
from .admin import PullRequestAdmin
from django.contrib.auth import get_user_model
from .models import PullRequest, is_there_migrations_to_make
from django.conf import settings

User = get_user_model()


class AdminTests(TestCase):
    fixtures = ['icon']

    def test_admin(self):
        user = User.objects.create(username='test', email='test@test.com')
        user.is_staff = True
        user.save()
        pull_request = PullRequest.objects.create(
            number=999,
            author=user,
            commits=0,
            additions=0,
            deletions=0,
            changed_files=0,
            merged_at=timezone.now(),
            received_at=timezone.now(),
            pulled_at=timezone.now(),
        )
        qs = PullRequest.objects.all()
        admin = PullRequestAdmin(model=PullRequest, admin_site=AdminSite)
        request = RequestFactory().get('/admin/')
        request.user = user
        admin.deploy(request, qs)
        self.assertTrue(PullRequest.objects.filter(id=pull_request.id).get().deployed)


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

    def test_deploy(self):
        self.pull_request.deploy()
