from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Icon)
admin.site.register(models.Notification)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['deadline', 'name', 'created_by', 'created_at', 'active']
    list_filter = ('created_by', 'created_at', 'active')


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary', 'dark', 'light']
    list_filter = ['name']


@admin.register(models.Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
        'active',
        'board',
        'order',
        'auto_status',
    ]
    list_filter = [
        'created_by',
        'created_at',
        'active',
        'auto_status',
    ]


@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
        'active',
        'bucket',
        'order',
        'status',
    ]
    list_filter = [
        'created_by',
        'created_at',
        'status',
        'active',
    ]


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
        'active',
        'card',
        'order',
        'checked_by',
        'checked_at',
    ]
    list_filter = [
        'created_by',
        'created_at',
        'active',
        'checked_by',
        'checked_at',
    ]


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
        'active',
        'board',
    ]
    list_filter = [
        'created_by',
        'created_at',
        'active',
        'board',
    ]


@admin.register(models.TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
        'active',
        'card',
        'started_at',
        'stopped_at',
        'duration',
    ]
    list_filter = [
        'created_by',
        'created_at',
        'active',
    ]


@admin.register(models.Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'project',
        'created_by',
        'accepted_by',
        'accepted_at',
    ]
    list_filter = [
        'email',
        'project',
        'created_by',
        'accepted_by',
        'accepted_at',
    ]
