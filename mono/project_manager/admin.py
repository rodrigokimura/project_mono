"""Project manager's admin"""
from django.contrib import admin

from . import models

admin.site.register(models.Icon)


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["deadline", "name", "created_by", "created_at", "active"]
    list_filter = ("created_by", "created_at", "active")
    search_fields = ["name"]
    actions = ("sort",)

    @admin.action(description="Sort boards")
    def sort(self, request, queryset):
        """Reset board order"""
        for project in queryset:
            project.sort()


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at", "order")
    list_filter = ("created_by", "created_at", "active")
    search_fields = ["name"]


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ["name", "primary", "dark", "light"]
    list_filter = ["name"]


@admin.register(models.Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "created_at",
        "active",
        "board",
        "order",
        "auto_status",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "active",
        "auto_status",
    ]
    search_fields = ["name"]


@admin.register(models.Card)
class CardAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "created_at",
        "active",
        "bucket",
        "order",
        "status",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "status",
        "active",
    ]
    search_fields = ["name"]


@admin.register(models.CardFile)
class CardFileAdmin(admin.ModelAdmin):
    list_display = ["id", "file", "card"]
    list_filter = ["file", "card"]


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "created_at",
        "active",
        "card",
        "order",
        "checked_by",
        "checked_at",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "active",
        "checked_by",
        "checked_at",
    ]
    search_fields = ["name"]


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "color",
        "created_by",
        "created_at",
        "active",
        "board",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "active",
        "board",
    ]
    search_fields = ["name"]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "text",
        "created_by",
        "created_at",
        "card",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "card",
    ]
    search_fields = ["text"]


@admin.register(models.TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "created_at",
        "active",
        "card",
        "started_at",
        "stopped_at",
        "duration",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "active",
    ]


@admin.register(models.Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "project",
        "created_by",
        "accepted_by",
        "accepted_at",
    ]
    list_filter = [
        "email",
        "project",
        "created_by",
        "accepted_by",
        "accepted_at",
    ]


@admin.register(models.Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ["name", "order", "created_by", "created_at", "active"]
    list_filter = ("name", "created_by", "created_at", "active")
    search_fields = ["name"]


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        "verbose_text",
        "card",
        "action",
        "context",
        "created_by",
        "created_at",
    ]
    list_filter = ["action", "created_by", "created_at"]
