import logging
import os

from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver

from .models import User, UserProfile


@receiver(post_save, sender=User, dispatch_uid="email_verification")
def email_verification(sender, instance, created, **kwargs):
    if created:
        profile: UserProfile = UserProfile.objects.create(
            user=instance,
        )
        profile.generate_initials_avatar()
        profile.send_verification_email()


@receiver(pre_delete, sender=UserProfile, dispatch_uid="delete_profile_picture")
def delete_profile_picture(sender, instance: UserProfile, using, **kwargs):

    def _delete_file(path):
        """ Deletes file from filesystem. """
        if os.path.isfile(path):
            os.remove(path)
    try:
        _delete_file(instance.avatar.path)
    except ValueError:
        logging.warning('No file found')
