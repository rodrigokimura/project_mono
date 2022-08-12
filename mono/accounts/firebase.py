from django.conf import settings
from firebase_admin import credentials, initialize_app
from firebase_admin.messaging import (
    MulticastMessage, Notification as FirebaseNotification, send_multicast,
)


if settings.FIREBASE_AUTH_FILE.exists():
    cred = credentials.Certificate(str(settings.FIREBASE_AUTH_FILE))
    initialize_app(cred)

def send_notification(title, message, tokens):
    firebase_notification = FirebaseNotification(title=title, body=message)
    try:
        result = send_multicast(
            MulticastMessage(
                data={'title': title, 'message': message},
                notification=firebase_notification,
                tokens=tokens
            )
        )
    except ValueError as exc:
        print(exc)
