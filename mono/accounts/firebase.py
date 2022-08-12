import logging

from django.conf import settings
from firebase_admin import credentials, initialize_app
from firebase_admin.messaging import (
    BatchResponse, MulticastMessage, Notification as FirebaseNotification,
    send_multicast,
)

logger = logging.getLogger(__name__)


if settings.FIREBASE_AUTH_FILE.exists():
    cred = credentials.Certificate(str(settings.FIREBASE_AUTH_FILE))
    initialize_app(cred)


def send_notification(title, message, tokens):
    firebase_notification = FirebaseNotification(title=str(title), body=message)
    try:
        result: BatchResponse = send_multicast(
            MulticastMessage(
                data={'title': str(title), 'message': str(message)},
                notification=firebase_notification,
                tokens=tokens
            )
        )
        logger.info(f'Messages sent via FCM: {result.success_count}')
    except ValueError as exc:
        logger.error(str(exc))
