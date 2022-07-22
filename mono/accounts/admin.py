"""Accounts' admin"""
from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.signals import post_save

from .models import (
    Feature, Notification, Plan, Subscription, User, UserProfile,
)


class UserAdmin(admin.ModelAdmin):
    """User admin"""

    actions = ['force_initial_setup']

    def force_initial_setup(self, request, queryset):  # pylint: disable=no-self-use
        """Force initial setup for selected users"""
        for user in queryset:
            post_save.send(User, instance=user, created=True)

    force_initial_setup.short_description = "Force initial setup"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """UserProfile admin"""

    def generate_avatar(self, request, queryset):  # pylint: disable=no-self-use
        """Generate avatar for selected users"""
        for profile in queryset:
            profile.generate_initials_avatar()

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
    """Notification admin"""

    def read(self, request, queryset: QuerySet[Notification]):  # pylint: disable=no-self-use
        """Mark notifications as read"""
        for notification in queryset:
            notification.mark_as_read()

    def duplicate(self, request, queryset: QuerySet[Notification]):  # pylint: disable=no-self-use
        """Duplicate notifications"""
        for notification in queryset:
            notification.pk = None
            notification.save()

    def send_to_telegram(self, request, queryset: QuerySet[Notification]):  # pylint: disable=no-self-use
        """Send notifications to telegram"""
        for notification in queryset:
            notification.send_to_telegram()

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


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        "product_id",
        "name",
        "type",
        "order"
    ]
    list_filter = [
        "type",
    ]
    ordering = ('order',)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = [
        "plan",
        "short_description",
        "icon",
        "display",
    ]
    list_filter = [
        "plan",
        "display",
    ]
    ordering = ('plan',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "plan",
        "created_at",
        "updated_at",
        "cancel_at",
        "event_id",
    ]
    list_filter = [
        "user",
        "plan",
        "created_at",
        "updated_at",
        "cancel_at",
    ]
