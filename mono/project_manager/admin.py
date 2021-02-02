from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Board)
admin.site.register(models.Bucket)
admin.site.register(models.Card)
admin.site.register(models.Item)

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['deadline', 'name', 'created_by', 'created_at', 'active']
    list_filter = ('created_by', 'created_at', 'active') 
