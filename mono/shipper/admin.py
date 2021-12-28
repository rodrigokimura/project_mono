from django.contrib import admin

from . import models


@admin.register(models.Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'first_name_a',
        'last_name_a',
        'first_name_b',
        'last_name_b',
        'created_at',
    ]
    list_filter = [
        'id',
        'first_name_a',
        'last_name_a',
        'first_name_b',
        'last_name_b',
        'created_at',
    ]
