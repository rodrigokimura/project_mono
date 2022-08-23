"""Admin page for background tasks models"""
from background_task.models import CompletedTask, Task
from django.contrib import admin

# pylint: disable=unused-argument


def inc_priority(modeladmin, request, queryset):
    """Increase task priority"""
    for obj in queryset:
        obj.priority += 1
        obj.save()


inc_priority.short_description = "priority += 1"


def dec_priority(modeladmin, request, queryset):
    """Decrease task priority"""
    for obj in queryset:
        obj.priority -= 1
        obj.save()


dec_priority.short_description = "priority -= 1"


class TaskAdmin(admin.ModelAdmin):
    display_filter = ["task_name"]
    search_fields = [
        "task_name",
        "task_params",
    ]
    list_display = [
        "task_name",
        "task_params",
        "run_at",
        "priority",
        "attempts",
        "has_error",
        "locked_by",
        "locked_by_pid_running",
    ]
    actions = [inc_priority, dec_priority]


class CompletedTaskAdmin(admin.ModelAdmin):
    display_filter = ["task_name"]
    search_fields = [
        "task_name",
        "task_params",
    ]
    list_display = [
        "task_name",
        "task_params",
        "run_at",
        "priority",
        "attempts",
        "has_error",
        "locked_by",
        "locked_by_pid_running",
    ]


admin.site.register(Task, TaskAdmin)
admin.site.register(CompletedTask, CompletedTaskAdmin)
