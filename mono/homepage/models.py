"""Homepage's models"""
from django.db import models


class Module(models.Model):
    """Group of things to easily activate"""

    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
