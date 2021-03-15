from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Transaction, Account, Category, Group
import datetime
from django.contrib.auth.models import AnonymousUser, User

# Create your tests here.
User = get_user_model()

class TransactionModelTests(TestCase):
  
    def test_signed_ammount_with_income(self):
        category = Category(type=Category.INCOME)
        income = Transaction(
            ammount=10,
            category=category)
        self.assertIs(income.signed_ammount > 0, True)

    def test_signed_ammount_with_expense(self):
        category = Category(type=Category.EXPENSE)
        expense = Transaction(
            ammount=10,
            category=category)
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

class AccountModelTests(TestCase):

    fixtures = ["icon.json"]

    def setUp(self):
        self.user_1 = User.objects.create(username="User_1")
        self.user_2 = User.objects.create(username="User_2")
        self.group = Group.objects.create(
            name="Group", 
            owned_by=self.user_1,
            created_by=self.user_1
        )
        self.assertIsNotNone(self.group)
        self.group.members.add(self.user_1)
        self.assertEquals(self.group.members.count(), 1)
        self.group.members.add(self.user_2)
        self.assertGreater(self.group.members.count(), 1)
        self.account = Account.objects.filter(owned_by=self.user_1).first()
        self.factory = RequestFactory()


    def test_group_creation(self):
        self.assertTrue(self.group.owned_by==self.user_1)
        self.assertFalse(self.group.owned_by==self.user_2)

    def test_patch_with_logged_in_user(self):
        
        transaction = Transaction.objects.create(
            description="Test", 
            ammount=100, 
            account=self.account,
            created_by=self.user_1,
            category=Category.objects.filter(created_by=self.user_1, type=Category.EXPENSE).first()
        )
        request = self.factory.get(f'/fn/transaction/{transaction.pk}/delete/')
        request.user = self.user_1

        # # Test my_view() as if it were deployed at /customer/details
        # response = my_view(request)
        # # Use this syntax for class-based views.
        # response = MyView.as_view()(request)
        # self.assertEqual(response.status_code, 200)

# User default accounts creation
# User default category creation