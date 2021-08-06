from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Item)
admin.site.register(models.Theme)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['deadline', 'name', 'created_by', 'created_at', 'active']
    list_filter = ('created_by', 'created_at', 'active')


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
