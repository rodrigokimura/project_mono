"""Command to create avatars for users without profile or avatar."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ...models import UserProfile


class Command(BaseCommand):
    """Command to create avatars for users without profile or avatar."""

    help = "Command to create avatars for users without profile or avatar."

    def handle(self, *args, **options):
        try:
            for user in get_user_model().objects.all():
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if profile.avatar is None:
                    profile.generate_initials_avatar()
        except Exception as any_exception:  # pylint: disable=broad-except
            raise CommandError(repr(any_exception)) from any_exception
