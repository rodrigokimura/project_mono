from django.db import models

# Create your models here.
class Module(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.name