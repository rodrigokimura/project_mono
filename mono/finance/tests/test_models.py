from http import HTTPStatus

import pytest
import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ..models import Account, Category, Group, Icon, Transaction
from ..views import AccountCreateView


class TestTransactionModel:

    def test_signed_amount_with_income(self):
        category = Category(type=Category.INCOME)
        income = Transaction(
            amount=10,
            category=category)
        assert income.signed_amount > 0

    def test_signed_amount_with_expense(self):
        category = Category(type=Category.EXPENSE)
        expense = Transaction(
            amount=10,
            category=category)
        assert expense.signed_amount < 0


@pytest.mark.django_db
class TestUserModel:

    def test_user_created(self, user):
        assert user is not None

    def test_user_has_accounts(self, user):
        assert Account.objects.filter(created_by=user).count() > 0

    def test_user_has_categories(self, user):
        assert Category.objects.filter(created_by=user).count() > 0


class AccountModelTests(TestCase):

    def setUp(self):
        Icon.create_defaults()
        self.user = User.objects.create(
            username="teste")
        self.factory = RequestFactory()

    def test_adjust_balance(self):
        account = Account.objects.filter(created_by=self.user).first()
        self.assertEqual(account.current_balance, 0)

        account.adjust_balance(100, self.user)
        self.assertGreater(account.current_balance, 0)

        account.adjust_balance(-100, self.user)
        self.assertLess(account.current_balance, 0)


class AccountFormTests(TestCase):

    def setUp(self):
        Icon.create_defaults()
        self.user = User.objects.create(username="teste")
        self.factory = RequestFactory()

    def test_get(self):
        request = self.factory.get('/fn/account/')
        request.user = self.user
        response = AccountCreateView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post(self):
        request = self.factory.post(
            path='/fn/account/',
            data={
                "name": "Teste",
            }
        )
        request.user = self.user
        response = AccountCreateView.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UserCreationTests(TestCase):

    def setUp(self):
        Icon.create_defaults()
        self.user_1 = User.objects.create(username="User_1")
        self.user_2 = User.objects.create(username="User_2")
        self.group = Group.objects.create(
            name="Group",
            owned_by=self.user_1,
            created_by=self.user_1
        )
        self.assertIsNotNone(self.group)
        self.group.members.add(self.user_1)
        self.assertEqual(self.group.members.count(), 1)
        self.group.members.add(self.user_2)
        self.assertGreater(self.group.members.count(), 1)
        self.account = Account.objects.filter(owned_by=self.user_1).first()
        self.factory = RequestFactory()

    def test_group_creation(self):
        self.assertTrue(self.group.owned_by == self.user_1)
        self.assertFalse(self.group.owned_by == self.user_2)

    def test_patch_with_logged_in_user(self):

        transaction = Transaction.objects.create(
            description="Test",
            amount=100,
            account=self.account,
            created_by=self.user_1,
            category=Category.objects.filter(
                created_by=self.user_1, type=Category.EXPENSE
            ).first()
        )
        request = self.factory.get(f'/fn/transaction/{transaction.pk}/delete/')
        request.user = self.user_1


class StripeTests(TestCase):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    def setUp(self):
        Icon.create_defaults()
        self.user = User.objects.create(username="user")
        products = stripe.Product.list(limit=100, active=True).data
        self.products = [product for product in products if product.metadata.app == 'finance']

    def test_stripe_products(self):
        self.assertGreater(len(self.products), 0)

    def test_stripe_plans(self):
        for product in self.products:
            plans = stripe.Plan.list(product=product.id, limit=100).data
            self.assertGreater(len(plans), 0)
