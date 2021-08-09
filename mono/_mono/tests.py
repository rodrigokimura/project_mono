from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.conf import settings
from .admin import MyAdminSite
from .asgi import application as asgi_app
from .wsgi import application as wsgi_app
from .auth_backends import EmailOrUsernameModelBackend
from .context_processors import environment, language_extras


User = get_user_model()


class AdminTest(TestCase):

    fixtures = ["icon.json"]

    @classmethod
    def setUpTestData(cls):
        cls.username = "test_admin"
        cls.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=cls.username)
        user.set_password(cls.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        cls.user = user

    def test_get_app_list(self):
        admin_site = MyAdminSite()

        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = self.user

        app_list = admin_site.get_app_list(request)
        self.assertIsInstance(app_list, list)


class AsgiTest(TestCase):
    def test_asgi_application(self):
        self.assertIsNotNone(asgi_app)


class WsgiTest(TestCase):
    def test_wsgi_application(self):
        self.assertIsNotNone(wsgi_app)


class AuthBackEndsTest(TestCase):

    fixtures = ["icon.json"]

    @classmethod
    def setUpTestData(cls):
        cls.username = "test_admin"
        cls.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=cls.username)
        user.set_password(cls.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        cls.user = user

    def test_authenticate_method(self):
        authentication_backend = EmailOrUsernameModelBackend()
        factory = RequestFactory()
        request = factory.get('/admin/')
        user = authentication_backend.authenticate(
            request=request,
            username=self.username,
            password=self.password,
        )
        self.assertEqual(user, self.user)
        user = authentication_backend.authenticate(
            request=request,
        )
        self.assertIsNone(user)
        user = authentication_backend.authenticate(
            request=request,
            username=self.username,
            password=User.objects.make_random_password(),
        )
        self.assertIsNone(user)


class ContextProcessorsTest(TestCase):

    def test_environment_method(self):
        factory = RequestFactory()
        request = factory.get('/')
        context = environment(request=request)
        self.assertIn('APP_ENV', context)

    def test_language_extras_method(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.LANGUAGE_CODE = 'pt-br'
        context = language_extras(request=request)
        self.assertIn('LANGUAGE_EXTRAS', context)
        self.assertIn('tinyMCE_language', context)


class SettingsTest(TestCase):

    def test_secret_key(self):
        with self.settings(APP_ENV='PRD'):
            secret_key = settings.SECRET_KEY
            print(secret_key)
