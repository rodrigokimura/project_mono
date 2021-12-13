from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.Icon)
admin.site.register(models.Goal)


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "created_by",
        "created_at",
        "timestamp",
        "amount",
        "type",
        "category",
        "account",
        "active",
        "recurrent",
        "installment",
        "transference",
    ]
    list_filter = [
        "created_by",
        "created_at",
        "timestamp",
        "category__type",
        "category__name",
        "active",
    ]


@admin.register(models.RecurrentTransaction)
class RecurrentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "created_by",
        "timestamp",
        "amount",
        "type",
        "category",
        "account",
        "active",
        "frequency",
    ]
    list_filter = [
        "created_by",
        "timestamp",
        "category__type",
        "category__name",
        "active",
        "frequency",
    ]


@admin.register(models.Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "created_by",
        "timestamp",
        "total_amount",
        "category",
        "account",
    ]
    list_filter = [
        "created_by",
        "timestamp",
        "category__type",
        "category__name",
    ]


@admin.register(models.Transference)
class TransferenceAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "from_account",
        "to_account",
        "created_by",
        "timestamp",
        "amount",
    ]
    list_filter = [
        "from_account",
        "to_account",
        "created_by",
        "timestamp",
        "amount",
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


@admin.register(models.Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        "amount",
        "start_date",
        "end_date",
        "configuration",
    ]
    list_filter = [
        "amount",
        "start_date",
        "end_date",
        "configuration",
    ]


@admin.register(models.BudgetConfiguration)
class BudgetConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        "created_by",
        "amount",
        "frequency",
        "start_date",
    ]
    list_filter = [
        "created_by",
        "amount",
        "frequency",
        "start_date",
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


@admin.register(models.Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = [
        "type",
        "metric",
        "field",
        "axis",
        "category",
        "filters",
    ]
    list_filter = [
        "type",
        "metric",
        "field",
        "axis",
        "category",
        "filters",
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


@admin.register(models.Plan)
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


@admin.register(models.Feature)
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


@admin.register(models.Subscription)
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
