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


@admin.register(models.Request)
class RequestAdmin(admin.ModelAdmin):
    """
    Config for requests
    """

    list_display = [
        'id',
        'app_name',
        'url_name',
        'route',
        'started_at',
        'duration',
    ]
    list_filter = [
        'started_at',
    ]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Config for comments
    """

    list_display = [
        'id',
        'text',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'text',
        'created_by',
        'created_at',
    ]
