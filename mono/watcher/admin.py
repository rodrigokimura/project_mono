from django.contrib import admin

from . import models


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'host',
    ]
    list_filter = [
        'id',
        'host',
    ]


@admin.register(models.Ping)
class PingAdmin(admin.ModelAdmin):

    list_display = [
        'user_id',
        'event',
        'document_location',
        'referrer_location',
        'timestamp',
        'screen_resolution',
        'viewport',
        'document_title',
        'browser_name',
        'mobile_device',
        'duration',
    ]
    list_filter = [
        'site',
        'user_id',
        'event',
        'timestamp',
        'browser_name',
        'mobile_device',
        'document_title',
        'openpixel_js_version',
    ]
