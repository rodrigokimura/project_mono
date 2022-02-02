"""Curriculum Builder's admin"""
from django.contrib import admin

from . import models


@admin.register(models.Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
    )
    list_filter = (
        'first_name',
        'last_name',
    )
    search_fields = (
        'first_name',
        'last_name',
    )
