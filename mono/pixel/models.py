from datetime import date, timedelta
from django.db import models
from django.db.models.aggregates import Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.CharField(
        max_length=1024,
        null=True,
        help_text="Host of the URL. Port or userinfo should be ommited. https://en.wikipedia.org/wiki/URL"
    )
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def flush_pings(self):
        self.ping_set.all().delete()

    def get_online_users(self):
        return self.ping_set.filter(
            event='pageload',
            pageclose_timestamp__isnull=True,
            timestamp__date=date.today()
        ).values('user_id').distinct()

    def get_pings(self, initial_datetime=timezone.now() - timedelta(days=30), final_datetime=timezone.now()):
        return self.ping_set.filter(
            timestamp__date__gte=initial_datetime,
            timestamp__date__lte=final_datetime,
        )

    def get_visitors(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values('user_id').distinct()

    def get_views(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.filter(event='pageload')

    def get_avg_duration(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        qs = pings.exclude(duration__isnull=True)
        if qs.exists():
            return str(qs.aggregate(d=Avg('duration'))['d'])
        else:
            return '0:00:00.000'

    def get_bounce_rate(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        closed_sessions = pings.filter(
            event='pageload',
            duration__isnull=False
        )
        if not closed_sessions.exists():
            return 0

        visitors = self.get_visitors(pings=pings)

        bounces = 0
        for v in visitors:
            c = closed_sessions.filter(user_id=v['user_id']).values('document_location').distinct().count()
            if c == 1:
                bounces += 1

        return bounces / closed_sessions.count()

    def get_document_locations(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values('document_location').distinct()

    def get_referrer_locations(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values('referrer_location').distinct()

    def get_browsers(self, pings=None, **kwargs):
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values('browser_name').distinct()


class Ping(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=1024, null=True)
    event = models.CharField(max_length=1024, null=True)
    event_data = models.CharField(max_length=1024, null=True)
    openpixel_js_version = models.CharField(max_length=1024, null=True)
    document_location = models.CharField(max_length=1024, null=True)
    referrer_location = models.CharField(max_length=1024, null=True)
    timestamp = models.DateTimeField(null=True)
    encoding = models.CharField(max_length=1024, null=True)
    screen_resolution = models.CharField(max_length=50, null=True)
    viewport = models.CharField(max_length=50, null=True)
    document_title = models.CharField(max_length=1024, null=True)
    browser_name = models.CharField(max_length=1024, null=True)
    mobile_device = models.BooleanField(null=True)
    user_agent = models.CharField(max_length=1024, null=True)
    timezone_offset = models.IntegerField(null=True)
    utm_source = models.CharField(max_length=1024, null=True)
    utm_medium = models.CharField(max_length=1024, null=True)
    utm_term = models.CharField(max_length=1024, null=True)
    utm_content = models.CharField(max_length=1024, null=True)
    utm_campaign = models.CharField(max_length=1024, null=True)

    pageload_timestamp = models.DateTimeField(null=True)
    pageclose_timestamp = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)

    def __str__(self):
        return str(self.id)
