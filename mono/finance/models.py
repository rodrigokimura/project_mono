from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.enums import Choices
from django.utils import timezone

User = get_user_model()

# Create your models here.  
class Transaction(models.Model):

    INCOME = 'INC'
    EXPENSE = 'EXP'
    TRANSACTION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    description = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ammount = models.FloatField()
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.description

class Icon(models.Model):
    markup = models.CharField(max_length=50, unique=True)
    def __str__(self) -> str:
        return self.markup

class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ForeignKey(Icon, on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    def __str__(self) -> str:
        return self.name
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

class Group(models.Model):
    name = models.CharField(max_length=50)
    member = models.ManyToManyField(User)
    def __str__(self) -> str:
        return self.name
        
class Account(models.Model): 
    name = models.CharField(max_length=50)
    belongs_to = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self) -> str:
        return self.name