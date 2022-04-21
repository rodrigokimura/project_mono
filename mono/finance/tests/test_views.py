from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http.response import JsonResponse
from django.test import RequestFactory, TestCase
from django.test.client import Client
from django.utils import timezone

from ..forms import UniversalTransactionForm
from ..models import (
    Account, Category, Goal, Group, Icon, Installment, Invite,
    RecurrentTransaction, Transaction,
)
from ..views import CardOrderView, HomePageView, TransactionCreateView


class HomePageViewTests(TestCase):

    def setUp(self):
        Icon.create_defaults()
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

    def setUp(self):
        Icon.create_defaults()
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

    def setUp(self):
        Icon.create_defaults()
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
        response = c.post(f'/fn/transaction/{transaction.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Transaction.objects.filter(id=transaction.id).exists())

    def test_transaction_month_archive_view(self):
        Transaction.objects.create(
            description="test",
            created_by=self.user,
            amount=100,
            account=Account.objects.filter(created_by=self.user).last(),
            category=self.category
        )
        c = Client()
        c.force_login(self.user)
        year = timezone.now().strftime("%Y")
        month = timezone.now().strftime("%m")
        response = c.get(f'/fn/transactions/{year}/{month}/')
        self.assertEqual(response.status_code, 200)

    def test_transaction_month_archive_view_with_filters(self):
        Transaction.objects.create(
            description="test",
            created_by=self.user,
            amount=100,
            account=Account.objects.filter(created_by=self.user).last(),
            category=self.category
        )
        c = Client()
        c.force_login(self.user)
        year = timezone.now().strftime("%Y")
        month = timezone.now().strftime("%m")
        response = c.get(f'/fn/transactions/{year}/{month}/?category=1&account=1')
        self.assertEqual(response.status_code, 200)

    def test_recurrent_transaction_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/recurrent-transactions/')
        self.assertEqual(response.status_code, 200)

    def test_recurrent_transaction_delete_view(self):
        recurrent_transaction = RecurrentTransaction.objects.create(
            description='test',
            created_by=self.user,
            amount=100,
            category=self.category,
            account=Account.objects.filter(created_by=self.user).first(),
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/recurrent-transaction/{recurrent_transaction.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RecurrentTransaction.objects.filter(id=recurrent_transaction.id).exists())

    def test_recurrent_isntallment_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/installments/')
        self.assertEqual(response.status_code, 200)

    def test_installment_delete_view(self):
        installment = Installment.objects.create(
            description='test',
            created_by=self.user,
            total_amount=100,
            category=self.category,
            account=Account.objects.filter(created_by=self.user).first(),
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/installment/{installment.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RecurrentTransaction.objects.filter(id=installment.id).exists())

    def test_account_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/accounts/')
        self.assertEqual(response.status_code, 200)

    def test_account_list_view_with_filters(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/accounts/?group=1&member=1')
        self.assertEqual(response.status_code, 200)

    def test_account_update_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get(f'/fn/account/{Account.objects.filter(created_by=self.user).first().id}/')
        self.assertEqual(response.status_code, 200)

    def test_account_delete_view(self):
        account = Account.objects.create(
            name='test',
            created_by=self.user,
            owned_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/account/{account.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Account.objects.filter(id=account.id).exists())

    def test_group_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/groups/')
        self.assertEqual(response.status_code, 200)

    def test_group_list_view_with_filter(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/groups/?member=1')
        self.assertEqual(response.status_code, 200)

    def test_group_delete_view(self):
        group = Group.objects.create(
            name='test',
            created_by=self.user,
            owned_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/group/{group.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Group.objects.filter(id=group.id).exists())

    def test_category_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/categories/')
        self.assertEqual(response.status_code, 200)

    def test_category_list_view_with_filter(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/categories/?type=INC')
        self.assertEqual(response.status_code, 200)

    def test_category_list_api(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/ajax/categories/')
        self.assertIn('success', response.json())
        self.assertTrue('success', response.json()['success'])

    def test_category_list_api_with_filter_type_only(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/ajax/categories/?type=INC')
        self.assertIn('success', response.json())
        self.assertTrue('success', response.json()['success'])

    def test_category_list_api_with_filters(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/ajax/categories/?type=INC&account=1')
        self.assertIn('success', response.json())
        self.assertTrue('success', response.json()['success'])

    def test_category_delete_view(self):
        category = Category.objects.create(
            name='test',
            icon=Icon.objects.first(),
            created_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/category/{category.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_goal_list_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/fn/goals/')
        self.assertEqual(response.status_code, 200)

    def test_goal_delete_view(self):
        goal = Goal.objects.create(
            name='teste',
            created_by=self.user,
            target_date=timezone.now(),
            target_amount=100,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/fn/goal/{goal.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Goal.objects.filter(id=goal.id).exists())


class IconViewTests(TestCase):

    def setUp(self) -> None:
        Icon.create_defaults()
        self.superuser = User.objects.create(username='test', email='test.test@test.com')
        self.superuser.is_superuser = True
        self.superuser.save()

    def test_icon_list_view(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.get('/fn/icons/')
        self.assertEqual(response.status_code, 200)

    def test_icon_create_view(self):
        c = Client()
        c.force_login(self.superuser)
        response = c.post('/fn/icon/', {'markup': 'asdasdads'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Icon.objects.filter(markup='asdasdads').exists())

    def test_icon_update_view(self):
        icon = Icon.objects.create(markup='test')
        c = Client()
        c.force_login(self.superuser)
        response = c.post(f'/fn/icon/{icon.id}/', {'markup': 'test2'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Icon.objects.filter(markup='test2').exists())

    def test_icon_delete_view(self):
        icon = Icon.objects.create(markup='test')
        c = Client()
        c.force_login(self.superuser)
        response = c.post(f'/fn/icon/{icon.id}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Icon.objects.filter(id=icon.id).exists())


class InviteTests(TestCase):

    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(username='test', email='test@test.com')
        self.group = Group.objects.create(
            name='test',
            created_by=self.user,
            owned_by=self.user,
        )

    def test_invite_api(self):
        c = Client()
        c.force_login(self.user)
        response = c.post('/fn/invite/', {
            'group': self.group.id,
            'email': 'test2@test.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Invite.objects.filter(
            group=self.group.id,
            email='test2@test.com',
        ).exists())

    def test_invite_api_existing_group_and_email(self):
        Invite.objects.create(
            group=self.group,
            email='test3@test.com',
            created_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post('/fn/invite/', {
            'group': self.group.id,
            'email': 'test3@test.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['message'], "You've already invited test3@test.com to this group.")


class ViewsetTests(TestCase):

    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(username='test', email='test@test.com')

    def test_viewset(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/fn/api/transactions/')
        self.assertEqual(r.status_code, 200)
