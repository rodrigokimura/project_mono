"""Checklists admin"""
from django.contrib import admin

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'checklist',
        'order',
        'description',
    ]
    list_filter = [
        'checklist',
        'order',
        'description',

    ]
    search_fields = ['description']


@admin.register(models.Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'name',
        'created_by',
        'created_at',

    ]
    search_fields = ['name']
    actions = ('sort',)

    @admin.action(description='Sort tasks')
    def sort(self, request, queryset):  # pylint: disable=no-self-use
        """Reset task order"""
        for checklist in queryset:
            checklist.sort()
