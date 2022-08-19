"""Checklists admin"""
from django.contrib import admin

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "description",
        "reminded",
        "next_task_created",
        "order",
        "checklist",
    ]
    list_filter = [
        "checklist",
        "order",
        "description",
    ]
    search_fields = ["description"]
    actions = ("remind",)

    @admin.action(description="Notify users of task reminders")
    def remind(self, request, queryset):
        """Notify users of task reminders"""
        for task in queryset:
            task.remind()


@admin.register(models.Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "name",
        "created_by",
        "created_at",
    ]
    search_fields = ["name"]
    actions = ("sort",)

    @admin.action(description="Sort tasks")
    def sort(self, request, queryset):
        """Reset task order"""
        for checklist in queryset:
            checklist.sort()
