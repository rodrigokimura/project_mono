from django.test import RequestFactory, TestCase
from django.views.generic.edit import FormView

from .models import List, User


class ViewTests(TestCase):

    fixtures = ['icon']

    def setUp(self) -> None:
        self.user = User.objects.create(username='test', email='test.test@test.com')
        self.client.force_login(self.user)

    def test_root_redirect_if_no_list(self):
        self.user.todo_lists.all().delete()
        response = self.client.get('/todo/')
        self.assertEqual(response.status_code, 302)

    def test_root(self):
        List.objects.create(name='test', created_by=self.user)
        response = self.client.get('/todo/')
        self.assertGreater(self.user.todo_lists.all().count(), 0)
        self.assertEqual(response.status_code, 200)
