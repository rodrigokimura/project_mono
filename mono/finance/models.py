from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.enums import Choices
from django.utils import timezone
from django.db.models import Sum

User = get_user_model()

INCOME = 'INC'
EXPENSE = 'EXP'
TRANSACTION_TYPES = [
    (INCOME, 'Income'),
    (EXPENSE, 'Expense'),
]

class Transaction(models.Model):
    description = models.CharField(max_length=50, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ammount = models.FloatField()
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    
    @property
    def signed_ammount(self):
        sign = 1
        if self.type == 'EXP':
            sign = -1
        return self.ammount*sign
        
    def __str__(self) -> str:
        return self.description

class Icon(models.Model):
    markup = models.CharField(max_length=50, unique=True)
    def __str__(self) -> str:
        return self.markup

class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, default=EXPENSE)
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
    initial_balance = models.FloatField(default=0)
    
    @property
    def current_balance(self):
        qs = Transaction.objects.filter(account=self.pk)
        sum = self.initial_balance
        for t in qs:
            sum += t.signed_ammount
        return sum
    
    @property
    def total_transactions(self):
        qs = Transaction.objects.filter(account=self.pk)
        return qs.count()
        
        
    def adjust_balance(self, target, user):
        diff = target - self.current_balance
        if diff < 0:
            type = "EXP"
        else:
            type = "INC"
        transaction = Transaction(ammount=abs(diff))
        transaction.description = "Balance adjustment"
        transaction.account = self
        transaction.created_by = user
        transaction.save()
        
    def __str__(self) -> str:
        return self.name