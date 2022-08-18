"""Curriculum Builder's admin"""
from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from . import models


@admin.register(models.Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
    )
    list_filter = (
        "first_name",
        "last_name",
    )
    search_fields = (
        "first_name",
        "last_name",
    )


@admin.register(models.SocialMediaProfile)
class SocialMediaProfileAdmin(admin.ModelAdmin):
    list_display = (
        "platform",
        "link",
    )
    list_filter = (
        "platform",
        "link",
    )
    search_fields = (
        "platform",
        "link",
    )


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    list_filter = (
        "name",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )


@admin.register(models.WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "description",
    )
    list_filter = (
        "company",
        "description",
    )
    search_fields = (
        "company",
        "description",
    )


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
    )
    list_filter = (
        "name",
        "description",
    )
    search_fields = (
        "name",
        "description",
    )


@admin.register(models.Acomplishment)
class AcomplishmentAdmin(OrderedModelAdmin):
    list_display = (
        "title",
        "description",
        "work_experience",
        "order",
    )
    list_filter = (
        "title",
        "description",
    )
    search_fields = (
        "title",
        "description",
    )
