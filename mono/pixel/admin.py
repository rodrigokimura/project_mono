"""Pixel admin"""
from django.contrib import admin

from . import models


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    def flush_pings(self, request, queryset):  # pylint: disable=no-self-use
        for site in queryset:
            site.flush_pings()

    flush_pings.short_description = "Delete all pings"

    def undo_deletion(self, request, queryset):  # pylint: disable=no-self-use
        queryset.update(deleted_at=None)

    undo_deletion.short_description = "Undo deletion"

    list_display = [
        "id",
        "host",
    ]
    list_filter = [
        "id",
        "host",
    ]
    actions = [flush_pings, undo_deletion]


@admin.register(models.Ping)
class PingAdmin(admin.ModelAdmin):

    list_display = [
        "user_id",
        "event",
        "document_location",
        "referrer_location",
        "timestamp",
        "screen_resolution",
        "viewport",
        "document_title",
        "browser_name",
        "mobile_device",
        "duration",
    ]
    list_filter = [
        "site",
        "user_id",
        "event",
        "timestamp",
        "browser_name",
        "mobile_device",
        "document_title",
        "openpixel_js_version",
    ]
