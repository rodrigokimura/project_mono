from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Project)
admin.site.register(models.Board)
admin.site.register(models.Bucket)
admin.site.register(models.Card)
admin.site.register(models.Item)