from django.contrib import admin
from . import models

# Register your models here.


@admin.register(models.PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    # Admin Action Functions
    def deploy(modeladmin, request, queryset):
        for pr in queryset:
            pr.pull(link='')
            pr.deploy()
    # Action description
    deploy.short_description = "Pull and deploy"

    list_display = [
        "number",
        "author",
        "commits",
        "additions",
        "deletions",
        "changed_files",
        "merged_at",
        "received_at",
        "pulled_at",
        "deployed_at",
    ]
    list_filter = [
        "author",
    ]
