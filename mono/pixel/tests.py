from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory

from .admin import SiteAdmin
from .forms import SiteForm
from .models import Site

User = get_user_model()


class AdminTests(TestCase):

    fixtures = ['icon']

    def setUp(self):
        self.user = User.objects.create(username='test', email='test@test.com')
        self.user.is_staff = True
        self.user.save()
        self.admin = SiteAdmin(model=Site, admin_site=AdminSite)
        self.request = RequestFactory().get('/admin/')
        self.request.user = self.user

    def test_flush_pings(self):
        site = Site.objects.create(
            host="test",
            created_by=self.user,
        )
        qs = Site.objects.all()
        self.admin.flush_pings(self.request, qs)
        self.assertFalse(site.ping_set.exists())

    def test_undo_deletion(self):
        site: Site = Site.objects.create(
            host="test2",
            created_by=self.user,
        )
        site.soft_delete()
        qs = Site.objects.all()
        self.admin.undo_deletion(self.request, qs)
        self.assertGreater(Site.objects.filter(deleted_at__isnull=True).count(), 0)


class FormTests(TestCase):

    fixtures = ["icon"]

    def test_site_form(self):
        data = {
            'host': 'testhost.com',
        }
        response = self.client.post("/pixel/tags/new/", data=data)
        self.assertEqual(response.status_code, 302)
        user, created = User.objects.get_or_create(username='testeteste')
        request = RequestFactory().get('/pixel/tags/new/')
        request.user = user

        form = SiteForm(data=data, request=request)
        form.save()
        self.assertGreater(Site.objects.count(), 0)


class ViewTests(TestCase):

    def test_root_non_authenticated_user(self):
        response = self.client.get("/pixel/")
        self.assertEqual(response.status_code, 302)

    # def test_root_authenticated_user(self):
    #     response = self.client.get("/pixel/")
    #     self.assertEqual(response.status_code, 200)

    # def test_site_creation(self):
    #     response = self.client.get("/pixel/")
    #     self.assertEqual(response.status_code, 200)

    # def test_site_listing(self):
    #     response = self.client.get("/pixel/tags/")
    #     self.assertEqual(response.status_code, 200)
