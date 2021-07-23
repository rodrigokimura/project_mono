from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from . import models


admin.site.register(models.Note, MarkdownxModelAdmin)
