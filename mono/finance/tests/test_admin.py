from django.contrib.admin import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone

from ..admin import NotificationAdmin
from ..models import Notification, User


class AdminTests(TestCase):

    fixtures = ['icon']

    def test_notification_mark_as_unread_action(self):
        user = User.objects.create(username='test', email='test@test.com')
        user.is_staff = True
        user.save()
        notification = Notification.objects.create(
            title='Test',
            message='Testing notification',
            to=user
        )
        notification.read_at = timezone.now()
        notification.save()
        self.assertTrue(notification.read)
        qs = Notification.objects.filter(title='Test')
        admin = NotificationAdmin(model=Notification, admin_site=AdminSite)
        request = RequestFactory().get('/admin/')
        request.user = user
        admin.mark_as_unread(request, qs)
        self.assertFalse(qs.get().read)
