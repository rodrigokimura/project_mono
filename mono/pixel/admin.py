from django.contrib import admin
from . import models


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = ['id']


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
    ]
    list_filter = [
        'site',
        'user_id',
        'timestamp',
        'browser_name',
        'mobile_device',
        'document_title',
        'openpixel_js_version',
    ]
