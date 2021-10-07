from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ...models import UserProfile


class Command(BaseCommand):
    help = 'Command to create avatars for users without profile or avatar'

    def handle(self, *args, **options):
        try:
            for u in get_user_model().objects.all():
                qs = UserProfile.objects.filter(user=u)
                if qs.exists():
                    p: UserProfile = qs.get()
                else:
                    p: UserProfile = UserProfile.objects.create(user=u)
                if p.avatar is None:
                    p.generate_initials_avatar()
        except Exception as e:
            CommandError(repr(e))
