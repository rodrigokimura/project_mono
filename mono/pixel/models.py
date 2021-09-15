from django.db import models
import uuid


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id)


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
