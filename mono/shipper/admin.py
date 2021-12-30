from django.contrib import admin

from . import models


@admin.register(models.Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name_1',
        'name_2',
        'created_at',
    ]
    list_filter = [
        'id',
        'name_1',
        'name_2',
        'created_at',
    ]
