from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
import jwt
from ..models import Board, Bucket, Card, Item, Project, Invite, Theme


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
        request = c.post(
            path=f'/pm/api/projects/{project.id}/invites/',
            data={
                'email': 'teste.teste@teste.com',
                'project': project.id,
            }
        )
        self.assertEqual(request.status_code, 201)
        self.assertTrue(Invite.objects.filter(email='teste.teste@teste.com').exists())

    def test_project_list_view(self):
        c = Client()
        c.force_login(self.user)
        request = c.get('/pm/projects/')
        self.assertEqual(request.status_code, 200)

    def test_project_detail_view(self):
        project = Project.objects.create(name='test project 2', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        request = c.get(f'/pm/project/{project.id}/')
        self.assertEqual(request.status_code, 200)

    def test_project_update_view_get(self):
        project = Project.objects.create(name='test test', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        request = c.get(f'/pm/project/{project.id}/edit/')
        self.assertEqual(request.status_code, 200)

    def test_project_update_view_post(self):
        project = Project.objects.create(name='test test', created_by=self.user)
        c = Client()
        c.force_login(self.user)
        request = c.post(f'/pm/project/{project.id}/edit/', {'name': 'test test 2'})
        self.assertEqual(request.status_code, 302)
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
        request = c.get(f'/pm/project/{project.id}/board/{board.id}/')
        self.assertEqual(request.status_code, 200)

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
        request = c.get(f'/pm/project/{project.id}/board/{board.id}/')
        messages = list(get_messages(request.wsgi_request))
        self.assertEqual(request.status_code, 302)
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
        request = c.get(f'/pm/invites/accept/?t={token}')
        self.assertEqual(request.status_code, 200)

    def test_invite_acceptance_view_no_token(self):
        c = Client()
        c.force_login(self.user)
        request = c.get('/pm/invites/accept/')
        self.assertContains(request, 'error')

    def test_invite_acceptance_view_invalid_token(self):
        c = Client()
        c.force_login(self.user)
        self.assertRaises(
            jwt.exceptions.DecodeError,
            c.get,
            path='/pm/invites/accept/?t=invalid_token'
        )


class ProjectListApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")

    def test_project_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get('/pm/api/projects/')
        self.assertEqual(response.status_code, 200)

    def test_project_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post('/pm/api/projects/', {'name': 'test'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_project_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post('/pm/api/projects/', {'name': ''})
        self.assertEqual(response.status_code, 400)


class ProjectDetailApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")

    def test_project_detail_view_get(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{project.id}/')
        self.assertEqual(response.status_code, 200)

    def test_project_detail_view_get_not_allowed(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        User.objects.create_user(username="test2", email="test2@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test2', password='supersecret')
        request = c.get(f'/pm/api/projects/{project.id}/')
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')

    def test_project_detail_view_get_invalid_project(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get('/pm/api/projects/999999999/')
        self.assertEqual(response.status_code, 404)

    def test_project_detail_view_put(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            path=f'/pm/api/projects/{project.id}/',
            data={'name': 'test project changed'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test project changed')

    def test_project_detail_view_put_invalid_data(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            path=f'/pm/api/projects/{project.id}/',
            data={'name': 'verylongstringverylongstringverylongstringverylongstringverylongstring'},
        )
        self.assertEqual(response.status_code, 400)

    def test_project_detail_view_put_not_allowed(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        User.objects.create_user(username="test4", email="test4@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test4', password='supersecret')
        request = c.put(f'/pm/api/projects/{project.id}/', {'name': 'sdasdasd'})
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')

    def test_project_detail_view_delete(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        c = APIClient()
        c.login(username='test', password='supersecret')
        request = c.delete(f'/pm/api/projects/{project.id}/')
        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.json()['success'])

    def test_project_detail_view_delete_not_allowed(self):
        project = Project.objects.create(name='test project', created_by=self.user)
        User.objects.create_user(username="test5", email="test5@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test5', password='supersecret')
        request = c.delete(f'/pm/api/projects/{project.id}/')
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')


class BoardListApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)

    def test_board_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/')
        self.assertEqual(response.status_code, 200)

    def test_board_list_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_board_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_board_list_view_post_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_board_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)


class BoardDetailApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)

    def test_board_detail_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/')
        self.assertEqual(response.status_code, 200)

    def test_board_detail_view_get_invalid_board(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/9999999/')
        self.assertEqual(response.status_code, 404)

    def test_board_detail_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_board_detail_view_put(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_board_detail_view_put_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_board_detail_view_put_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_board_detail_view_patch(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.patch(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_board_detail_view_patch_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.patch(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_board_detail_view_patch_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.patch(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_board_detail_view_delete(self):
        board = Board.objects.create(name='test board to delete', created_by=self.user, project=self.project)
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{board.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Board.objects.filter(id=board.id).exists())

    def test_board_detail_view_delete_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')


class BucketListApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.theme = Theme.objects.first()

    def test_bucket_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/')
        self.assertEqual(response.status_code, 200)

    def test_bucket_list_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_bucket_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/',
            {'name': 'test', 'board': self.board.id, 'order': 1, 'color': self.theme.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_bucket_list_view_post_empty_color(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/',
            {'name': 'test', 'board': self.board.id, 'order': 1, 'color': ''})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_bucket_list_view_post_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_bucket_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)


class BucketDetailApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(
            name='test',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_bucket_detail_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/')
        self.assertEqual(response.status_code, 200)

    def test_bucket_detail_view_get_invalid_bucket(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/99999999/')
        self.assertEqual(response.status_code, 404)

    def test_bucket_detail_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_bucket_detail_view_put(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/',
            {'name': 'test', 'board': self.board.id, 'order': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_bucket_detail_view_put_with_color(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/',
            {'name': 'test', 'board': self.board.id, 'order': 1, 'color': self.theme.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_bucket_detail_view_put_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/',
            {'name': 'test', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_bucket_detail_view_put_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_bucket_detail_view_delete(self):
        bucket = Bucket.objects.create(
            name='test bucket to delete',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{bucket.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Bucket.objects.filter(id=bucket.id).exists())

    def test_bucket_detail_view_delete_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')


class CardListApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(name='test', created_by=self.user, board=self.board, order=1)
        self.theme = Theme.objects.first()

    def test_card_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/')
        self.assertEqual(response.status_code, 200)

    def test_card_list_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_card_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1, 'color': self.theme.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_card_list_view_post_empty_color(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1, 'color': ''})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_card_list_view_post_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/',
            {'name': 'test', 'bucket': self.bucket.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_card_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)


class CardDetailApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(
            name='test',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.card = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=self.bucket,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_card_detail_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/')
        self.assertEqual(response.status_code, 200)

    def test_card_detail_view_get_invalid_card(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/9999999/')
        self.assertEqual(response.status_code, 404)

    def test_card_detail_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_card_detail_view_put(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_card_detail_view_put_completed(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1, 'status': Bucket.COMPLETED})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], Bucket.COMPLETED)

    def test_card_detail_view_put_in_progress(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1, 'status': Bucket.IN_PROGRESS})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], Bucket.IN_PROGRESS)

    def test_card_detail_view_put_with_color(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': 'test', 'bucket': self.bucket.id, 'order': 1, 'color': self.theme.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_card_detail_view_put_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': 'test', 'bucket': self.bucket.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_card_detail_view_put_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_card_detail_view_delete(self):
        card = Card.objects.create(
            name='test bucket to delete',
            created_by=self.user,
            bucket=self.bucket,
            order=1,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{card.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Card.objects.filter(id=card.id).exists())

    def test_card_detail_view_delete_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')


class ItemListApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(name='test', created_by=self.user, board=self.board, order=1)
        self.card = Card.objects.create(name='test', created_by=self.user, bucket=self.bucket, order=1)
        self.theme = Theme.objects.first()

    def test_item_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/')
        self.assertEqual(response.status_code, 200)

    def test_item_list_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_item_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/',
            {'name': 'test', 'card': self.card.id, 'order': 1})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'test')

    def test_item_list_view_post_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/',
            {'name': 'test', 'card': self.card.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_item_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)


class ItemDetailApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(
            name='test',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.card = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=self.bucket,
            order=1,
        )
        self.item = Item.objects.create(
            name='test',
            created_by=self.user,
            card=self.card,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_item_detail_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/')
        self.assertEqual(response.status_code, 200)

    def test_item_detail_view_get_invalid_item(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/${self.card.id}/items/999999/')
        self.assertEqual(response.status_code, 404)

    def test_item_detail_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_item_detail_view_put(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/',
            {'name': 'test', 'card': self.card.id, 'order': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'test')

    def test_item_detail_view_put_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/',
            {'name': 'test', 'card': self.card.id})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')

    def test_item_detail_view_put_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/',
            {'name': ''})
        self.assertEqual(response.status_code, 400)

    def test_item_detail_view_delete(self):
        item = Item.objects.create(
            name='test item to delete',
            created_by=self.user,
            card=self.card,
            order=1,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{item.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_item_detail_view_delete_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.delete(f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/items/{self.item.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(str(response.json()), 'User not allowed')


class CardMoveApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.source_bucket = Bucket.objects.create(
            name='source',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.target_bucket = Bucket.objects.create(
            name='target',
            created_by=self.user,
            board=self.board,
            order=2,
        )
        self.card = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=self.source_bucket,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_card_move(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': self.target_bucket.id,
                'order': 2,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_auto_status_completed(self):
        target_bucket_auto_status = Bucket.objects.create(
            name='target',
            created_by=self.user,
            board=self.board,
            order=2,
            auto_status=Bucket.COMPLETED,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': target_bucket_auto_status.id,
                'order': 2,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_auto_status_not_started(self):
        target_bucket_auto_status = Bucket.objects.create(
            name='target',
            created_by=self.user,
            board=self.board,
            order=2,
            auto_status=Bucket.NOT_STARTED,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': target_bucket_auto_status.id,
                'order': 2,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_auto_status_in_progress(self):
        target_bucket_auto_status = Bucket.objects.create(
            name='target',
            created_by=self.user,
            board=self.board,
            order=2,
            auto_status=Bucket.IN_PROGRESS,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': target_bucket_auto_status.id,
                'order': 2,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_more_cards_same_bucket(self):
        bucket = Bucket.objects.create(
            name='test',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        card_1 = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=bucket,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=bucket,
            order=2,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=bucket,
            order=3,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': bucket.id,
                'target_bucket': bucket.id,
                'order': 2,
                'card': card_1.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_more_cards_different_buckets(self):
        source_bucket = Bucket.objects.create(
            name='source_bucket_2',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        target_bucket = Bucket.objects.create(
            name='target_bucket_2',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        card_1 = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=source_bucket,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=source_bucket,
            order=2,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=source_bucket,
            order=3,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=target_bucket,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=target_bucket,
            order=2,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': source_bucket.id,
                'target_bucket': target_bucket.id,
                'order': 2,
                'card': card_1.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_card_move_invalid_card(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': self.target_bucket.id,
                'order': 2,
                'card': 9999999
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['card'][0], 'Invalid card')

    def test_card_move_invalid_order(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': self.target_bucket.id,
                'order': -1,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['order'][0], 'Invalid order')

    def test_card_move_invalid_source_bucket(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': 999999,
                'target_bucket': self.target_bucket.id,
                'order': 1,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['source_bucket'][0], 'Invalid bucket')

    def test_card_move_invalid_target_bucket(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': 99999,
                'order': 1,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['target_bucket'][0], 'Invalid bucket')

    def test_card_move_user_not_allowed_in_source_bucket(self):
        user = User.objects.create_user(username="not_allowed_source_bucket", email="test@test.com", password="supersecret")
        project = Project.objects.create(name='not_allowed_source_bucket', created_by=user)
        board = Board.objects.create(name='not_allowed_source_bucket', created_by=user, project=project)
        not_allowed_source_bucket = Bucket.objects.create(
            name='not_allowed_source_bucket',
            created_by=user,
            board=board,
            order=1,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': not_allowed_source_bucket.id,
                'target_bucket': self.target_bucket.id,
                'order': 1,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0], 'User not allowed')

    def test_card_move_user_not_allowed_in_target_bucket(self):
        user = User.objects.create_user(username="not_allowed_target_bucket", email="test@test.com", password="supersecret")
        project = Project.objects.create(name='not_allowed_target_bucket', created_by=user)
        board = Board.objects.create(name='not_allowed_target_bucket', created_by=user, project=project)
        not_allowed_target_bucket = Bucket.objects.create(
            name='not_allowed_target_bucket',
            created_by=user,
            board=board,
            order=1,
        )
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/card_move/',
            data={
                'source_bucket': self.source_bucket.id,
                'target_bucket': not_allowed_target_bucket.id,
                'order': 1,
                'card': self.card.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0], 'User not allowed')


class BucketMoveApiViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(
            name='bucket',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_bucket_move(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': self.board.id,
                'order': 2,
                'bucket': self.bucket.id
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['order'], 2)

    def test_bucket_move_invalid_bucket(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': self.board.id,
                'order': 2,
                'bucket': 99999
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['bucket'][0], 'Invalid bucket')

    def test_bucket_move_invalid_board(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': 99999,
                'order': 2,
                'bucket': self.bucket.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['board'][0], 'Invalid board')

    def test_bucket_move_invalid_order(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': self.board.id,
                'order': -1,
                'bucket': self.bucket.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['order'][0], 'Invalid order')

    def test_bucket_move_user_not_allowed(self):
        User.objects.create_user(username="not_allowed", email="not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='not_allowed', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': self.board.id,
                'order': 1,
                'bucket': self.bucket.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0], 'User not allowed')

    def test_bucket_move_bucket_outside_board(self):
        outside_board = Board.objects.create(name='outside_board', created_by=self.user, project=self.project)
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path='/pm/api/bucket_move/',
            data={
                'board': outside_board.id,
                'order': 1,
                'bucket': self.bucket.id
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['non_field_errors'][0], 'Bucket outside board')


class StartStopTimerAPIViewTests(APITestCase):
    fixtures = [
        "icon",
        "project_manager_icons",
        "project_manager_themes",
    ]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.board = Board.objects.create(name='test', created_by=self.user, project=self.project)
        self.bucket = Bucket.objects.create(
            name='bucket',
            created_by=self.user,
            board=self.board,
            order=1,
        )
        self.card = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=self.bucket,
            order=1,
        )
        self.theme = Theme.objects.first()

    def test_start_stop_timer(self):
        """Test timer starting and then stopping"""
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path=f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/timer/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        response = c.post(
            path=f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/timer/',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_start_stop_timer_invalid_card(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(
            path=f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/99999/timer/',
        )
        self.assertEqual(response.status_code, 404)

    def test_start_stop_timer_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(
            path=f'/pm/api/projects/{self.project.id}/boards/{self.board.id}/buckets/{self.bucket.id}/cards/{self.card.id}/timer/',
        )
        self.assertEqual(response.status_code, 403)


class InviteListApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)

    def test_invite_list_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/invites/')
        self.assertEqual(response.status_code, 200)

    def test_invite_list_view_get_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/invites/')
        self.assertEqual(response.status_code, 403)

    def test_invite_list_view_post(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(f'/pm/api/projects/{self.project.id}/invites/',
                          {'email': 'test@test.com', 'project': self.project.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['email'], 'test@test.com')

    def test_invite_list_view_post_not_allowed(self):
        User.objects.create_user(username="test_not_allowed", email="test_not_allowed@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test_not_allowed', password='supersecret')
        response = c.post(f'/pm/api/projects/{self.project.id}/invites/',
                          {'email': 'test@test.com', 'project': self.project.id})
        self.assertEqual(response.status_code, 403)

    def test_invite_list_view_post_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.post(f'/pm/api/projects/{self.project.id}/invites/')
        self.assertEqual(response.status_code, 400)


class InviteDetailApiViewTests(APITestCase):
    fixtures = ["icon", "project_manager_icons"]

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.invite = Invite.objects.create(email="test@test.com", project=self.project)

    def test_invite_detail_view_get(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/')
        self.assertEqual(response.status_code, 200)

    def test_invite_detail_view_get_invalid_invite(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.get(f'/pm/api/projects/{self.project.id}/invites/999999/')
        self.assertEqual(response.status_code, 404)

    def test_invite_detail_view_get_not_allowed(self):
        User.objects.create_user(username="test2", email="test2@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test2', password='supersecret')
        request = c.get(f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/')
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')

    def test_invite_detail_view_put(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            path=f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/',
            data={'email': 'asd@asd.com', 'project': self.project.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], 'asd@asd.com')

    def test_invite_detail_view_put_invalid_data(self):
        c = APIClient()
        c.login(username='test', password='supersecret')
        response = c.put(
            path=f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/',
            data={'name': 'verylongstringverylongstringverylongstringverylongstringverylongstring'},
        )
        self.assertEqual(response.status_code, 400)

    def test_invite_detail_view_put_not_allowed(self):
        User.objects.create_user(username="test4", email="test4@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test4', password='supersecret')
        request = c.put(f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/', {'name': 'sdasdasd'})
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')

    def test_invite_detail_view_delete(self):
        invite = Invite.objects.create(email="test_delete@test.com", project=self.project)
        c = APIClient()
        c.login(username='test', password='supersecret')
        request = c.delete(f'/pm/api/projects/{self.project.id}/invites/{invite.id}/')
        self.assertEqual(request.status_code, 204)

    def test_invite_detail_view_delete_not_allowed(self):
        User.objects.create_user(username="test5", email="test5@test.com", password="supersecret")
        c = APIClient()
        c.login(username='test5', password='supersecret')
        request = c.delete(f'/pm/api/projects/{self.project.id}/invites/{self.invite.id}/')
        self.assertEqual(request.status_code, 403)
        self.assertEqual(str(request.json()), 'User not allowed')


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
