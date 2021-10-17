from django.contrib import admin
from django.db.models import QuerySet

from .models import Notification, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    def generate_avatar(self, request, queryset):
        for p in queryset:
            p.generate_initials_avatar()

    generate_avatar.short_description = "Generate avatar picture"

    list_display = [
        'user',
        'avatar',
        'verified_at',
    ]
    list_filter = [
        'user',
        'avatar',
        'verified_at',
    ]
    actions = [generate_avatar]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    def read(self, request, queryset: QuerySet[Notification]):
        for n in queryset:
            n.mark_as_read()

    def duplicate(self, request, queryset: QuerySet[Notification]):
        for n in queryset:
            n.pk = None
            n.save()

    read.short_description = "Mark notification as read"
    duplicate.short_description = "Clone notifications"

    list_display = [
        'title',
        'to',
        'created_at',
        'icon',
        'read_at',
        'action_url',
    ]
    list_filter = [
        'title',
        'to',
        'created_at',
        'icon',
        'read_at',
        'action_url',
    ]
    actions = [read, duplicate]
