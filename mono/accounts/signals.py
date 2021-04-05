from .models import User, UserProfile


def email_verification(sender, instance, created, **kwargs):
    if created and sender == User:
        profile = UserProfile.objects.create(
            user=instance,
        )
        profile.send_verification_email()
