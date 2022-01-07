from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ..permissions import IsCreator


class ObjMock:
    def __init__(self, user):
        self.created_by = user


class PermissionTests(TestCase):
    fixtures = ['icon']

    def test_user_with_permission(self):
        request = RequestFactory().get('/')
        user = User.objects.create(username='testuser')
        request.user = user
        obj = ObjMock(user)
        has_permission = IsCreator().has_object_permission(request, None, obj)
        self.assertTrue(has_permission)

    def test_user_without_permission(self):
        request = RequestFactory().get('/')
        user = User.objects.create(username='testuser')
        not_permitted_user = User.objects.create(username='not_permitted')
        request.user = not_permitted_user
        obj = ObjMock(user)
        has_permission = IsCreator().has_object_permission(request, None, obj)
        self.assertFalse(has_permission)
