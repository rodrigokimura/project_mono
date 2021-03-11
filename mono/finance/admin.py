from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Group)
admin.site.register(models.Icon)
admin.site.register(models.Category)
admin.site.register(models.Account)
admin.site.register(models.Goal)
admin.site.register(models.Budget)
admin.site.register(models.Invite)

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