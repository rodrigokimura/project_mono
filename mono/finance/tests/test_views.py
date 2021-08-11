from django.utils import timezone
from django.http.response import JsonResponse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import Client
from ..views import HomePageView, CardOrderView, TransactionCreateView
from ..models import Account, Category, Icon, Installment, RecurrentTransaction, Transaction
from ..forms import UniversalTransactionForm
from django.contrib.messages.storage.fallback import FallbackStorage


class HomePageViewTests(TestCase):
    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(
            username='jacob', email='jacob@test.com', password='top_secret')

    def test_homepage(self):
        request = RequestFactory().get('/fn/')
        request.user = self.user
        response = HomePageView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        request = RequestFactory().get('/fn/')
        request.user = self.user
        view = HomePageView()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn('total_balance', context)
        self.assertIn('expenses_this_month', context)
        self.assertIn('incomes_this_month', context)
        self.assertIn('expenses_last_month', context)
        self.assertIn('incomes_last_month', context)
        self.assertIn('closed_budgets', context)
        self.assertIn('open_budgets', context)
        request.user = AnonymousUser()
        view.setup(request)
        context = view.get_context_data()
        self.assertNotIn('total_balance', context)


class CardOrderViewTests(TestCase):
    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(
            username='test_card_order', email='test_card_order@test.com', password='top_secret')

    def test_context_data(self):
        request = RequestFactory().get('/')
        request.user = self.user
        view = CardOrderView()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn('cards', context)

    def test_context_data_with_all_cards_in_config(self):
        user = User.objects.create(
            username='test_card_order_2', email='test_card_order_2@test.com', password='top_secret')
        user.configuration.cards = '1,2,3'
        user.configuration.save()
        request = RequestFactory().get('/')
        request.user = user
        view = CardOrderView()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn('cards', context)

    def test_context_data_with_two_cards_in_config(self):
        user = User.objects.create(
            username='test_card_order_3', email='test_card_order_3@test.com', password='top_secret')
        user.configuration.cards = '1,2'
        user.configuration.save()
        request = RequestFactory().get('/')
        request.user = user
        view = CardOrderView()
        view.setup(request)
        context = view.get_context_data()
        self.assertIn('cards', context)

    def test_post(self):
        c = Client()
        c.force_login(user=self.user)
        r = c.post('/fn/card-order/', {'cards': '1'})
        self.assertIsInstance(r, JsonResponse)


class TransactionListViewTests(TestCase):

    fixtures = ['icon.json']

    def setUp(self):
        self.user = User.objects.create(username='test', email='test.test@test.com')
        self.category = Category.objects.create(
            name='test',
            created_by=self.user,
            description='test',
            type='INC',
            icon=Icon.objects.last()
        )
        Transaction.objects.create(
            description="test",
            created_by=self.user,
            amount=100,
            account=Account.objects.filter(created_by=self.user).last(),
            category=Category.objects.last()
        )

    def test_transaction_list_view(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/fn/transactions/')
        self.assertEqual(r.status_code, 200)

    def test_transaction_list_view_with_filters(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/fn/transactions/?category=1&account=1')
        self.assertEqual(r.status_code, 200)

    def test_transaction_list_view_with_page(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/fn/transactions/?page=1')
        self.assertEqual(r.status_code, 200)

    def test_transaction_create_view(self):
        c = Client()
        c.force_login(self.user)
        data = {
            'description': 'test',
            'type': self.category.type,
            'amount': 100,
            'category': self.category.id,
            'account': 1,
            'timestamp': timezone.now(),
            'active': True,
            'handle_remainder': Installment.FIRST,
            'months': 12,
            'frequency': RecurrentTransaction.MONTHLY,
        }
        r = c.post('/fn/transaction/', data)
        self.assertEqual(r.status_code, 302)

    def test_transaction_create_view_type_TRF(self):
        c = Client()
        c.force_login(self.user)
        data = {
            'type': 'TRF',
            'amount': '100',
            'description': 'test',
            'account': "",
            'category': "",
            'from_account': Account.objects.filter(created_by=self.user).first(),
            'to_account': Account.objects.filter(created_by=self.user).last(),
            'timestamp': timezone.now(),
            'active': 'on',
            'frequency': RecurrentTransaction.MONTHLY,
            'months': '12',
            'handle_remainder': Installment.FIRST,
        }
        request = RequestFactory().post('/fn/transaction/', data)
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        view = TransactionCreateView()
        view.setup(request)
        form = UniversalTransactionForm(data, request=request)
        form.is_valid()
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

    def test_transaction_create_view_recurrent(self):
        c = Client()
        c.force_login(self.user)
        data = {
            'type': self.category.type,
            'amount': '100',
            'description': 'test',
            'account': Account.objects.filter(created_by=self.user).first(),
            'category': self.category,
            'timestamp': timezone.now(),
            'active': 'on',
            'frequency': RecurrentTransaction.MONTHLY,
            'months': '12',
            'handle_remainder': Installment.FIRST,
            'is_recurrent_or_installment': True,
            'recurrent_or_installment': 'R',
        }
        request = RequestFactory().post('/fn/transaction/', data)
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        view = TransactionCreateView()
        view.setup(request)
        form = UniversalTransactionForm(data, request=request)
        form.is_valid()
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

    def test_transaction_create_view_installment(self):
        c = Client()
        c.force_login(self.user)
        data = {
            'type': self.category.type,
            'amount': '100',
            'description': 'test',
            'account': Account.objects.filter(created_by=self.user).first(),
            'category': self.category,
            'timestamp': timezone.now(),
            'active': 'on',
            'frequency': RecurrentTransaction.MONTHLY,
            'months': '12',
            'handle_remainder': Installment.FIRST,
            'is_recurrent_or_installment': True,
            'recurrent_or_installment': 'I',
        }
        request = RequestFactory().post('/fn/transaction/', data)
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        view = TransactionCreateView()
        view.setup(request)
        form = UniversalTransactionForm(data, request=request)
        form.is_valid()
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)

    def test_transaction_delete_view(self):
        transaction = Transaction.objects.create(
            description="test",
            created_by=self.user,
            amount=100,
            account=Account.objects.filter(created_by=self.user).last(),
            category=self.category
        )
        c = Client()
        c.force_login(self.user)
        data = {
            'type': self.category.type,
            'amount': '100',
            'description': 'test',
            'account': Account.objects.filter(created_by=self.user).first(),
            'category': self.category,
            'timestamp': timezone.now(),
            'active': 'on',
            'frequency': RecurrentTransaction.MONTHLY,
            'months': '12',
            'handle_remainder': Installment.FIRST,
            'is_recurrent_or_installment': True,
            'recurrent_or_installment': 'I',
        }
        request = RequestFactory().post('/fn/transaction/', data)
        request.user = self.user
        setattr(request, 'session', 'session')
        setattr(request, '_messages', FallbackStorage(request))
        view = TransactionCreateView()
        view.setup(request)
        form = UniversalTransactionForm(data, request=request)
        form.is_valid()
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 302)
