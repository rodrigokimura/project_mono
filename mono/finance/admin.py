from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Icon)
admin.site.register(models.Goal)
admin.site.register(models.Budget)

@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "created_by",
        "created_at",
        "timestamp",
        "ammount",
        "type",
        "category",
        "account",
        "active",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "timestamp",
        "type",
        "category__name",
        "active",
    ]

@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "created_by",
        "owned_by",
    ]
    list_filter = [
        "name",
        "created_by",
        "owned_by",
        "members",
    ]

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "type",
        "created_by",
        "group",
        "icon",
        "active",
    ]
    list_filter = [
        "name",
        "description",
        "type",
        "created_by",
        "group",
        "icon",
        "active",
    ]

@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "owned_by",
        "created_by",
        "group",
        "initial_balance",
    ]
    list_filter = [
        "name",
        "owned_by",
        "created_by",
        "group",
        "initial_balance",
    ]

@admin.register(models.Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = [
        "created_by",
        "created_at",
        "group",
        "email",
        "accepted",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "group",
        "email",
        "accepted",
    ]

@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "message",
        "icon",
        "to",
        "read_at",
        "action",
        "active",
    ]
    list_filter = [
        "title",
        "message",
        "icon",
        "to",
        "read_at",
        "action",
        "active",
    ]

@admin.register(models.Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "main_page",
    ]
    list_filter = [
        "user",
        "main_page",
    ]

