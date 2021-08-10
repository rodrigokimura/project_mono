from datetime import timedelta
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.test import TestCase
import jwt
from finance.models import Notification
from .models import User, UserProfile, user_directory_path
from .forms import UserCreateForm, UserProfileForm


class UserCreateFormTest(TestCase):

    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(
            username="test_user",
            email='test@test.com'
        )

    def test_username_field_label(self):
        form = UserCreateForm()
        self.assertTrue(form.fields['username'].label is None or form.fields['username'].label == 'Display name')

    def test_email_field_label(self):
        form = UserCreateForm()
        self.assertTrue(form.fields['email'].label is None or form.fields['email'].label == 'Email address')

    def test_form_clean(self):
        data = {
            'username': 'testclient',
            'email': 'test@test.com',
            'password1': 'qweasd@123',
            'password2': 'qweasd@123',
        }
        form = UserCreateForm(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0], 'Email exists')
        data = {
            'username': 'username',
            'email': 'randomemail@test.com',
            'password1': 'test@123',
            'password2': 'test@123',
        }
        form = UserCreateForm(data)
        self.assertTrue(form.is_valid())


class UserProfileFormTest(TestCase):

    def test_username_field_label(self):
        form = UserProfileForm()
        self.assertTrue(form.fields['avatar'].label is None or form.fields['avatar'].label == 'Avatar')


class UserProfileModelTests(TestCase):

    fixtures = ['icon.json']

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )

    def test_methods(self):
        user_profile = UserProfile.objects.get(user=self.user)

        self.assertIsNotNone(user_profile)

        self.assertEqual(
            user_directory_path(user_profile, "filename"),
            f'user_{self.user.id}/filename'
        )
        self.assertEqual(user_profile.__str__(), user_profile.user.username)

        user_profile.send_verification_email()
        self.assertTrue(
            Notification.objects.filter(
                to=self.user,
                message="We've sent you an email to verify your account."
            ).exists()
        )
        user_profile.verify()
        self.assertTrue(
            Notification.objects.filter(
                to=self.user,
                message="Your account was successfully verified."
            ).exists()
        )


class UserProfileViewTests(TestCase):

    fixtures = ['icon.json']

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )

    def test_account_verification_view(self):
        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=30),
                "user_id": self.user.id
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        c = Client()
        r = c.get(f'/accounts/verify?t={token}')
        self.assertContains(r, "accepted")
        r = c.get('/accounts/verify?t=')
        self.assertContains(r, "error")

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
        r = c.post('/accounts/login-as', {'user': superuser.id})
        self.assertContains(r, f"Successfully logged in as {superuser.username}")
