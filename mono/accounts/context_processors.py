"""Accounts' context processors"""


def unread_notification_count(request):
    """Get the number of unread notifications for the current user."""
    if not request.user.is_authenticated:
        return {}
    qs = request.user.notifications.filter(read_at__isnull=True)
    if qs.exists():
        count = qs.count()
        timestamp = qs.last().created_at
    else:
        count = 0
        timestamp = None
    return {
        'unread_notification_count': count,
        'unread_notification_timestamp': timestamp,
    }
