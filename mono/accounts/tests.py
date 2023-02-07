from datetime import timedelta
from unittest.mock import MagicMock, Mock

import jwt
import pytest
from django.conf import settings
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import timezone
from finance.models import Icon

from .context_processors import unread_notification_count
from .forms import UserProfileForm
from .models import Notification, User, UserProfile, user_directory_path
from .telegram import send_message


@pytest.fixture
def mocked_post(monkeypatch):
    my_mock = Mock()
    monkeypatch.setattr("requests.post", my_mock)
    return my_mock


def test_telegram(mocked_post: Mock, settings):

    chat_id = 123
    text = "fake message"
    token = 123
    settings.TELEGRAM_BOT_TOKEN = token

    send_message(chat_id, text)

    mocked_post.assert_called_once_with(
        f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
    )


def test_telegram_without_token_should_do_nothing(mocked_post: Mock, settings):

    chat_id = 123
    text = "fake message"
    settings.TELEGRAM_BOT_TOKEN = None

    send_message(chat_id, text)

    mocked_post.assert_not_called()


class TestUserProfileForm:
    def test_username_field_label(self):
        form = UserProfileForm()
        assert (
            form.fields["avatar"].label is None
            or form.fields["avatar"].label == "Avatar"
        )


@pytest.mark.django_db
class TestUserProfileModel:
    def test_methods(self, user):
        user_profile: UserProfile = UserProfile.objects.get(user=user)

        assert user_profile is not None

        assert (
            user_directory_path(user_profile, "filename")
            == f"user_{user.id}/filename"
        )

        assert user_profile.__str__() == user_profile.user.username

        user_profile.send_verification_email()

        assert Notification.objects.filter(
            to=user, message="We've sent you an email to verify your account."
        ).exists()

        user_profile.verify()
        assert Notification.objects.filter(
            to=user, message="Your account was successfully verified."
        ).exists()

    def test_generate_initials_avatar_exception(self, user):
        def _save(*args, **kwargs):
            raise OSError("test")

        user_profile: UserProfile = UserProfile.objects.get(user=user)
        user_profile.avatar.save = MagicMock(side_effect=_save)
        user_profile.generate_initials_avatar()
        user_profile.avatar.save.assert_called()


class UserProfileViewTests(TestCase):
    def setUp(self):
        Icon.create_defaults()
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )

    def test_account_verification_view(self):
        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=30),
                "user_id": self.user.id,
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        c = Client()
        r = c.get(f"/accounts/verify/?t={token}")
        self.assertContains(r, "accepted")
        r = c.get("/accounts/verify/?t=")
        self.assertContains(r, "error")


@pytest.mark.django_db
class TestContextProcessor:
    @pytest.fixture
    def default_icons(self):
        Icon.create_defaults()

    def test_user_context_processor(self, default_icons):
        request = RequestFactory().get("/")
        user = User.objects.create(username="test")
        request.user = user
        context = unread_notification_count(request)
        assert context["unread_notification_count"] == 1

    def test_user_context_processor_no_notifications(self, default_icons):
        request = RequestFactory().get("/")
        user = User.objects.create(username="test")
        user.notifications.all().delete()
        request.user = user
        context = unread_notification_count(request)
        assert context["unread_notification_count"] == 0
