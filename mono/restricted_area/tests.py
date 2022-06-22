from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from finance.models import Icon

User = get_user_model()


class RestrictedAreaViewTests(TestCase):

    def setUp(self):
        Icon.create_defaults()
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )

    def test_login_as_view(self):
        superuser = User.objects.create(
            username="super",
            email="super@test.com",
        )
        superuser.is_superuser = True
        superuser.set_password('supersecret')
        superuser.save()
        c = Client()
        c.login(username=superuser.username, password='supersecret')
        r = c.post('/restricted-area/login-as/', {'user': superuser.id})
        self.assertContains(r, f"Successfully logged in as {superuser.username}")
