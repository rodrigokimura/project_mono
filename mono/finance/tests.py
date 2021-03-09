from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Transaction, Account, Category
import datetime

User = get_user_model()
# Create your tests here.

class TransactionModelTests(TestCase):
  
    def test_signed_ammount_with_income(self):
        income = Transaction(
            ammount=10,
            type="INC")
        self.assertIs(income.signed_ammount > 0, True)

    def test_signed_ammount_with_expense(self):
        expense = Transaction(
            ammount=10,
            type="EXP")
        self.assertIs(expense.signed_ammount < 0, True)
        
class UserModelTests(TestCase):
  
    fixtures = ["icon.json"]
    
    def setUp(self):
        self.user = User.objects.create(
            username="teste")

    def test_user_created(self):
        self.assertIsNotNone(self.user)

    def test_user_has_accounts(self):
        self.assertGreater(Account.objects.filter(created_by=self.user).count(),0)

    def test_user_has_categories(self):
        self.assertGreater(Category.objects.filter(created_by=self.user).count(),0)
    
class AccountModelTests(TestCase):
    
    fixtures = ["icon.json"]
    
    def setUp(self):
        self.user = User.objects.create(
            username="teste")
            
    def test_adjust_balance(self):
        account = Account.objects.filter(created_by=self.user).first()
        self.assertEquals(account.current_balance, 0)
        
        account.adjust_balance(100, self.user)
        self.assertGreater(account.current_balance, 0)

        account.adjust_balance(-100, self.user)
        self.assertLess(account.current_balance, 0)


# User default accounts creation
# User default category creation