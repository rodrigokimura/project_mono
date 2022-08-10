"""Accounts' signals"""
import logging
import os

from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver

from .models import Notification, User, UserProfile


@receiver(post_save, sender=User, dispatch_uid="initial_user_setup")
def initial_user_setup(sender, instance, created, **kwargs):
    """
    Send verification email and generate avatar for new users
    """
    if created and sender == User:
        profile, created = UserProfile.objects.get_or_create(
            user=instance,
        )
        profile.generate_initials_avatar()
        profile.send_verification_email()


@receiver(pre_delete, sender=UserProfile, dispatch_uid="delete_profile_picture")
def delete_profile_picture(sender, instance: UserProfile, **kwargs):
    """Delete avatar file when profile is deleted"""
    if sender == UserProfile:
        def _delete_file(path):
            """ Deletes file from filesystem. """
            if os.path.isfile(path):
                os.remove(path)
        try:
            _delete_file(instance.avatar.path)
        except ValueError:
            logging.warning('No file found')


@receiver(post_save, sender=Notification, dispatch_uid="send_notification")
def send_notification(sender, instance: Notification, created, **kwargs):
    if created and sender == Notification:
        instance.send_to_telegram()
