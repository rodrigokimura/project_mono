"""Todo list admin"""
from django.contrib import admin

from . import models

admin.site.register(models.Checklist)
admin.site.register(models.Task)
