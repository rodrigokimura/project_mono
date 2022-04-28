from django.test import TestCase
from finance.models import Icon

from .models import Checklist, User


class ViewTests(TestCase):

    def setUp(self) -> None:
        Icon.create_defaults()
        self.user = User.objects.create(username='test', email='test.test@test.com')
        self.client.force_login(self.user)

    def test_root_redirect_if_no_list(self):
        self.user.checklists.all().delete()
        response = self.client.get('/cl/')
        self.assertEqual(response.status_code, 302)

    def test_root(self):
        Checklist.objects.create(name='test', created_by=self.user)
        response = self.client.get('/cl/')
        self.assertGreater(self.user.checklists.all().count(), 0)
        self.assertEqual(response.status_code, 200)
