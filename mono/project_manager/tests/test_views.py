from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.test.client import Client
from ..models import Project, Invite
# from ..views import BoardCreateView


class ViewTests(TestCase):
    fixtures = ["icon.json"]

    def setUp(self) -> None:
        self.user = User.objects.create(username="test", email="test@test.com")

    def test_create_project_view(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/pm/project/')
        self.assertEqual(response.status_code, 200)
        response = c.post('/pm/project/', {'name': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='test', created_by=self.user).exists())

    def test_send_invite(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        r = c.post(
            path=f'/pm/api/projects/{project.id}/invites/',
            data={'email': 'teste.teste@teste.com'}
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Invite.objects.filter(email='teste.teste@teste.com').exists())


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

    # def test_only_allowed_users_can_create_boards(self):
    #     user = User.objects.create(
    #         username="test_user_2")
    #       .post(
    #         path='/pm/project/1/board/',
    #         data={
    #             'name': 'board',
    #             'project': 1,
    #         }
    #     )
    #     request.user = user
    #     response = BoardCreateView.as_view()(request)
        # self.assertEqual(response.status_code, 200)
