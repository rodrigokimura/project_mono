from datetime import timedelta
from unittest.mock import MagicMock

import jwt
from django.conf import settings
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import timezone

from .context_processors import unread_notification_count
from .forms import UserCreateForm, UserProfileForm
from .models import Notification, User, UserProfile, user_directory_path


class UserCreateFormTest(TestCase):

    fixtures = ["icon"]

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

    fixtures = ['icon']

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )

    def test_methods(self):
        user_profile: UserProfile = UserProfile.objects.get(user=self.user)

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

    def test_generate_initials_avatar_exception(self):

        def _save(*args, **kwargs):
            raise OSError('test')

        user_profile: UserProfile = UserProfile.objects.get(user=self.user)
        user_profile.avatar.save = MagicMock(side_effect=_save)
        user_profile.generate_initials_avatar()
        user_profile.avatar.save.assert_called()


class UserProfileViewTests(TestCase):

    fixtures = ['icon']

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
        r = c.get(f'/accounts/verify/?t={token}')
        self.assertContains(r, "accepted")
        r = c.get('/accounts/verify/?t=')
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
        r = c.post('/accounts/login-as/', {'user': superuser.id})
        self.assertContains(r, f"Successfully logged in as {superuser.username}")


class ContextProcessorTests(TestCase):

    fixtures = ['icon']

    def test_user_context_processor(self):
        request = RequestFactory().get('/')
        user = User.objects.create(username="test")
        request.user = user
        context = unread_notification_count(request)
        self.assertEqual(context['unread_notification_count'], 1)

    def test_user_context_processor_no_notifications(self):
        request = RequestFactory().get('/')
        user = User.objects.create(username="test")
        user.notifications.all().delete()
        request.user = user
        context = unread_notification_count(request)
        self.assertEqual(context['unread_notification_count'], 0)
