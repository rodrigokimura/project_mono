"""Django admin config for Watcher"""
from django.contrib import admin

from . import models


@admin.register(models.Issue)
class IssueAdmin(admin.ModelAdmin):
    """
    Config for issues
    """

    list_display = [
        'id',
        'name',
        'description',
        'created_at',
    ]
    list_filter = [
        'name',
        'description',
        'created_at',
    ]


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    """
    Config for events
    """

    list_display = [
        'id',
        'timestamp',
        'user',
    ]
    list_filter = [
        'timestamp',
        'user',
    ]


@admin.register(models.Traceback)
class TracebackAdmin(admin.ModelAdmin):
    """
    Config for tracebacks
    """

    list_display = [
        'issue',
        'order',
        'file_name',
        'function_name',
        'line_number',
        'variables',
    ]
    list_filter = [
        'issue',
        'order',
        'file_name',
        'function_name',
        'line_number',
    ]
