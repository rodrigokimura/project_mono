from django.contrib import admin

from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "title",
        "author",
        "created_at",
        "updated_at",
    ]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "post",
        "author",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "post",
        "author",
        "created_at",
        "updated_at",
    ]
