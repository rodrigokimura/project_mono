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
        'name_1',
        'name_2',
        'created_at',
    ]
    search_fields = [
        'name_1',
        'name_2',
    ]


@admin.register(models.Portmanteau)
class PortmanteauAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'ship',
        '__str__',
    ]
    list_filter = [
        'id',
    ]
    search_fields = [
        'ship__name_1',
        'ship__name_2',
    ]
