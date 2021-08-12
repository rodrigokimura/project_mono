from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.utils import timezone
# from rest_framework.test import APIRequestFactory
# from rest_framework.test import force_authenticate
from rest_framework.test import APIClient
import jwt
from ..models import Board, Project, Invite
from ..views import ProjectDetailAPIView


class ViewTests(TestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create(username="test", email="test@test.com")

    def test_create_project_view_get(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/pm/project/')
        self.assertEqual(response.status_code, 200)

    def test_create_project_view_post(self):
        c = Client()
        c.force_login(self.user)
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

    def test_project_list_view(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/pm/projects/')
        self.assertEqual(r.status_code, 200)

    def test_project_detail_view(self):
        project = Project.objects.create(name='test project 2', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        r = c.get(f'/pm/project/{project.id}/')
        self.assertEqual(r.status_code, 200)

    def test_project_update_view_get(self):
        project = Project.objects.create(name='test test', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        r = c.get(f'/pm/project/{project.id}/edit/')
        self.assertEqual(r.status_code, 200)

    def test_project_update_view_post(self):
        project = Project.objects.create(name='test test', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        r = c.post(f'/pm/project/{project.id}/edit/', {'name': 'test test 2'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Project.objects.filter(name='test test 2').exists())

    def test_board_detail_view(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        board = Board.objects.create(
            name='test board',
            created_by=self.user,
            project=project,
        )
        c = Client()
        c.force_login(self.user)
        r = c.get(f'/pm/project/{project.id}/board/{board.id}/')
        self.assertEqual(r.status_code, 200)

    def test_board_detail_view_not_assigned_user(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        board = Board.objects.create(
            name='test board',
            created_by=self.user,
            project=project,
        )
        c = Client()
        user_2 = User.objects.create(username="test_2", email="test@test2.com")
        c.force_login(user_2)
        r = c.get(f'/pm/project/{project.id}/board/{board.id}/')
        messages = list(get_messages(r.wsgi_request))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You are not assigned to this board!')

    def test_board_create_view_get(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        response = c.get(f'/pm/project/{project.id}/board/')
        self.assertEqual(response.status_code, 200)

    def test_board_create_view_post(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/pm/project/{project.id}/board/', {
            'name': 'test board creation',
            'project': project.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Board.objects.filter(name='test board creation', created_by=self.user).exists())

    def test_board_update_view_get(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        board = Board.objects.create(
            name='test project',
            project=project,
            created_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.get(f'/pm/project/{project.id}/board/{board.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_board_update_view_post(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        board = Board.objects.create(
            name='test project',
            project=project,
            created_by=self.user,
        )
        c = Client()
        c.force_login(self.user)
        response = c.post(f'/pm/project/{project.id}/board/{board.id}/edit/', {
            'name': 'test board modification',
            'project': project.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Board.objects.filter(name='test board modification', created_by=self.user).exists())

    def test_invite_acceptance_view(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        invite = Invite.objects.create(
            project=project,
            email='test3@test.com',
            created_by=self.user,
        )
        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=1),
                "id": invite.id,
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )
        c = Client()
        c.force_login(self.user)
        r = c.get(f'/pm/invites/accept/?t={token}')
        self.assertEqual(r.status_code, 200)

    def test_invite_acceptance_view_no_token(self):
        c = Client()
        c.force_login(self.user)
        r = c.get('/pm/invites/accept/')
        self.assertContains(r, 'error')

    def test_invite_acceptance_view_invalid_token(self):
        c = Client()
        c.force_login(self.user)
        self.assertRaises(
            jwt.exceptions.DecodeError,
            c.get,
            path='/pm/invites/accept/?t=invalid_token'
        )


class ApiViewTests(TestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create(username="test", email="test@test.com")

    def test_project_list_view_get(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/pm/api/projects/')
        self.assertEqual(response.status_code, 200)

    def test_project_list_view_post(self):
        c = Client()
        c.force_login(self.user)
        response = c.post('/pm/api/projects/', {'name': 'test'})
        self.assertEqual(response.status_code, 201)

    def test_project_list_view_post_invalid_data(self):
        c = Client()
        c.force_login(self.user)
        response = c.post('/pm/api/projects/', {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_project_detail_view_get(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        response = c.get(f'/pm/api/projects/{project.id}/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_view_get_invalid_project(self):
        c = Client()
        c.force_login(self.user)
        response = c.get('/pm/api/projects/999999999/')
        self.assertEqual(response.status_code, 404)

    def test_project_detail_view_put(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        response = c.put(
            path=f'/pm/api/projects/{project.id}/',
            content_type='application/json',
            data={'name': 'test project changed'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test project changed')

    def test_project_detail_view_put_invalid_data(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        response = c.put(
            path=f'/pm/api/projects/{project.id}/',
            content_type='application/json',
            data={'name': ''},
        )
        self.assertEqual(response.status_code, 400)

    def test_project_detail_view_put_non_allowed_user(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        user_2 = User.objects.create(username="test2", email="test2@test.com")
        c = APIClient()
        c.force_authenticate(user_2)
        r = c.put(f'/pm/api/projects/{project.id}/', {'name': ''}, format='json')
        print(r)
        # print(response.json())
        # self.assertEqual(response.status_code, 200)


class PermissionTests(TestCase):

    fixtures = ["icon"]

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
