from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from .models import Project
from .views import BoardCreateView


class PermissionTests(TestCase):

    fixtures = ["icon.json"]

    def setUp(self):
        self.factory = RequestFactory()

    def test_anyone_can_create_projects(self):
        user = User.objects.create(
            username="test_user_1")
        project = Project.objects.create(
            created_by=user
        )
        self.assertIsNotNone(project)
        self.assertTrue(Project.objects.filter(created_by=user).exists())

    def test_only_allowed_users_can_create_boards(self):
        user = User.objects.create(
            username="test_user_2")
        request = self.factory.post('/pm/board/')
        request.user = user
        response = BoardCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)
