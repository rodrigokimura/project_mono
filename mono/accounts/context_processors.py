from django.conf import settings


def unread_notification_count(request):
    c = 0
    if request.user.is_authenticated:
        c = request.user.notifications.filter(read_at__isnull=True).count()
    return {
        'unread_notification_count': c
    }
