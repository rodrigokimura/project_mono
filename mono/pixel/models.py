"""Pixel's models"""
import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.aggregates import Avg
from django.utils import timezone

JS_SNIPPET = """<script>
    !function(e,t,n,p,i,o,a){e[p]||((i=e[p]=function(){i.process?i.process.apply(i,arguments):i.queue.push(arguments)}).queue=[],i.t=+new Date,(o=t.createElement(n)).async=1,o.src="%s/static/openpixel.js?t="+864e5*Math.ceil(new Date/864e5),(a=t.getElementsByTagName(n)[0]).parentNode.insertBefore(o,a))}(window,document,"script","opix"),opix("init","ID-%s"),opix("event","pageload");
</script>
"""


class Site(models.Model):
    """Group tracking information"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.CharField(
        max_length=1024,
        null=True,
        help_text="Host of the URL. Port or userinfo should be ommited. https://en.wikipedia.org/wiki/URL",
    )
    created_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return str(self.id)

    def soft_delete(self):
        """Mark site as unregistered"""
        self.deleted_at = timezone.now()
        self.save()

    @property
    def snippet(self):
        """Generate script tag customized for this site"""
        snippet = JS_SNIPPET % ("http://127.0.0.42:8080", self.id)
        return snippet.replace("/n", "").replace("/r", "").strip()

    def flush_pings(self):
        self.ping_set.all().delete()

    def get_online_users(self):
        """Get distinct users from unclosed sessions"""
        return (
            self.ping_set.filter(
                event="pageload",
                pageclose_timestamp__isnull=True,
                timestamp__gte=timezone.now() - timedelta(hours=24),
            )
            .values("user_id")
            .distinct()
        )

    def get_pings(
        self,
        initial_datetime=timezone.now() - timedelta(days=30),
        final_datetime=timezone.now(),
    ):
        """Get pings in a date range"""
        return self.ping_set.filter(
            timestamp__range=[initial_datetime, final_datetime],
        )

    def get_visitors(self, pings=None, **kwargs):
        """Get unique visitors in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values_list("user_id", flat=True).distinct()

    def get_views(self, pings=None, **kwargs):
        """Get page views in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.filter(event="pageload")

    def get_avg_duration(self, pings=None, **kwargs):
        """Get avg session durations in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        qs = pings.exclude(duration__isnull=True)
        if qs.exists():
            return str(qs.aggregate(d=Avg("duration"))["d"])
        return "0:00:00.000"

    def get_bounce_rate(self, pings=None, **kwargs):
        """Get bounce rate in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        closed_sessions = pings.filter(event="pageload", duration__isnull=False)
        if not closed_sessions.exists():
            return 0

        visitors = self.get_visitors(pings=pings)

        bounces = 0
        for visitor in visitors:
            closed_sessions_count = (
                closed_sessions.filter(user_id=visitor)
                .values("document_location")
                .distinct()
                .count()
            )
            bounces += 1 if closed_sessions_count == 1 else 0

        return bounces / closed_sessions.count()

    def get_document_locations(self, pings=None, **kwargs):
        """Get distinct document locations in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values("document_location").distinct()

    def get_referrer_locations(self, pings=None, **kwargs):
        """Get distinct referrer locations in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values("referrer_location").distinct()

    def get_browsers(self, pings=None, **kwargs):
        """Get distinct browsers in a date range"""
        if pings is None:
            pings = self.get_pings(**kwargs)
        return pings.values("browser_name").distinct()


class Ping(models.Model):
    """
    Tracked data for each pixel request
    """

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
