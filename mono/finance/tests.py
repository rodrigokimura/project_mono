from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Transaction, Account
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
        """
        """
        expense = Transaction(
            ammount=10,
            type="EXP")
        self.assertIs(expense.signed_ammount < 0, True)
        
class UserModelTests(TestCase):
  
    fixtures = ["icon.json"]
    
    def setUp(self):
        self.user = User.objects.create(
            username="teste")
        #user = UserManager.create_user(username="teste")
    
    def test_adjust_balance(self):
        
        self.assertIs(self.user is not None, True)