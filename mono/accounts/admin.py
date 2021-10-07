from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    def generate_avatar(self, request, queryset):
        for p in queryset:
            p.generate_initials_avatar()

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
