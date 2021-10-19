from django.conf import settings


def unread_notification_count(request):
    c = 0
    if request.user.is_authenticated:
        qs = request.user.notifications.filter(read_at__isnull=True)
        last = qs.last()
        if last:
            ts = last.created_at
        else:
            ts = None
    return {
        'unread_notification_count': qs.count(),
        'unread_notification_timestamp': ts,
    }
