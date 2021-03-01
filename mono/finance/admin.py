from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Transaction)
admin.site.register(models.Group)
admin.site.register(models.Icon)
admin.site.register(models.Category)
admin.site.register(models.Account)
admin.site.register(models.Goal)
admin.site.register(models.Budget)
admin.site.register(models.Invite)