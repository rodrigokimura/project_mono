from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class TransactionModel(models.Model):
    description = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.name
    class Meta:
        abstract = True

class Expense(TransactionModel):
    deadline = models.DateTimeField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects")

class Income(TransactionModel):
    deadline = models.DateTimeField()
    assigned_to = models.ManyToManyField(User, related_name="assigned_projects")

class Family(models.Model):
    deadline = models.DateTimeField()
    name = models.CharField(verbose_name="Nome", max_length=50)