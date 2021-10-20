def unread_notification_count(request):
    if request.user.is_authenticated:
        qs = request.user.notifications.filter(read_at__isnull=True)
        if qs.exists():
            count = qs.count()
            ts = qs.last().created_at
        else:
            count = 0
            ts = None
        return {
            'unread_notification_count': count,
            'unread_notification_timestamp': ts,
        }
    return {}
