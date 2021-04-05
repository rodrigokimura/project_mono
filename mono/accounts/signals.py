from .models import User, UserProfile


def initial_setup(sender, instance, created, **kwargs):
    if created and sender == User:
        UserProfile.objects.create(
            user=instance,
        )
