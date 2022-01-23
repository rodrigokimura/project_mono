"""Homepage's admin"""
from django.contrib import admin

from . import models

admin.site.register(models.Module)
