from django.http.response import JsonResponse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.test.client import Client
from ..views import HomePageView, CardOrderView


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
