from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Item)


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
    ]
    list_filter = [
        'created_by',
        'created_at',
        'active',
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
    ]
    list_filter = [
        'created_by',
        'created_at',
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
