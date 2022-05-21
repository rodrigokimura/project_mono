import pytest
from django.test import Client
from django.utils.timezone import now
from finance.models import Icon

from .models import Checklist, Task


@pytest.mark.django_db
class TestChecklists:

    @pytest.fixture
    def default_icons(self):
        Icon.create_defaults()

    @pytest.fixture
    def user(self, django_user_model, default_icons):
        return django_user_model.objects.create(username='test', email='test.test@test.com')

    @pytest.fixture
    def another_user(self, django_user_model, default_icons):
        return django_user_model.objects.create(username='anothertest', email='another.test@test.com')

    def test_str_checklist(self):
        checklist1 = Checklist(name='checklist1')
        assert str(checklist1) == 'checklist1'

    def test_str_task(self):
        checklist = Checklist(name='checklist1')
        task = Task(checklist=checklist, description='task1')
        assert str(task) == 'task1'

    def test_root(self, client: Client, user):
        Checklist.objects.create(name='test', created_by=user)
        client.force_login(user)
        response = client.get('/cl/')
        assert user.checklists.all().exists()
        assert response.status_code == 200

    def test_checklist_should_return_only_users_checklist(self, client: Client, user, another_user):
        checklist1 = Checklist.objects.create(name='test', created_by=user)
        Checklist.objects.create(name='test2', created_by=another_user)
        client.force_login(user)
        response = client.get('/cl/api/checklists/')
        assert response.status_code == 200
        assert response.json()['results'] == [{'id': checklist1.id, 'name': checklist1.name}]

    def test_task_should_return_only_users_checklist(self, client: Client, user, another_user):
        checklist1 = Checklist.objects.create(name='test', created_by=user)
        task1 = Task.objects.create(checklist=checklist1, description='test', created_by=user)
        checklist2 = Checklist.objects.create(name='test2', created_by=another_user)
        Task.objects.create(checklist=checklist2, description='test', created_by=another_user)
        client.force_login(user)
        response = client.get('/cl/api/tasks/')
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
        assert {
            'id': task1.id,
            'checklist': checklist1.id,
            'description': task1.description,
        }.items() <= response.json()['results'][0].items()

    def test_task_check_should_succeed(self, client: Client, user):
        checklist: Checklist = Checklist.objects.create(name='test', created_by=user)
        task: Task = Task.objects.create(checklist=checklist, description='test', created_by=user)
        client.force_login(user)
        response = client.post(f'/cl/api/tasks/{task.id}/check/')
        task.refresh_from_db()
        assert response.status_code == 204
        assert task.checked_at is not None
        assert task.checked_by == user

    def test_task_uncheck_should_succeed(self, client: Client, user):
        checklist: Checklist = Checklist.objects.create(name='test', created_by=user)
        task: Task = Task.objects.create(
            checklist=checklist,
            description='test',
            created_by=user,
            checked_by=user,
            checked_at=now(),
        )
        client.force_login(user)
        response = client.post(f'/cl/api/tasks/{task.id}/uncheck/')
        task.refresh_from_db()
        assert response.status_code == 204
        assert task.checked_at is None
        assert task.checked_by is None

    def test_create_checklist_should_succeed(self, client: Client, user):
        client.force_login(user)
        response = client.post(
            '/cl/api/checklists/',
            {
                'name': 'test',
            }
        )
        checklist = Checklist.objects.get(name='test')
        assert response.status_code == 201
        assert checklist.order == 1

    def test_create_task_should_succeed(self, client: Client, user):
        checklist = Checklist.objects.create(name='test', created_by=user)
        client.force_login(user)
        response = client.post(
            '/cl/api/tasks/',
            {
                'checklist': checklist.id,
                'description': 'test',
            }
        )
        task = Task.objects.get(description='test')
        assert response.status_code == 201
        assert task.order == 1

    def test_change_checklist_order_should_succeed(self, client: Client, user):
        for i in range(1, 5):
            Checklist.objects.create(id=i, name='test', created_by=user, order=i)
        client.force_login(user)
        response = client.post(
            '/cl/api/checklist-move/',
            {
                'checklist': 4,
                'order': 2,
            }
        )
        assert Checklist.objects.get(id=4).order == 2

    def test_change_task_order_should_succeed(self, client: Client, user):
        cl = Checklist.objects.create(id=1, name='test', created_by=user, order=1)
        for i in range(1, 5):
            Task.objects.create(
                checklist=cl,
                description='test',
                created_by=user,
                order=i
            )
        client.force_login(user)
        task = Task.objects.get(order=4)
        response = client.post(
            '/cl/api/task-move/',
            {
                'task': task.id,
                'order': 2,
            }
        )
        task.refresh_from_db()
        assert task.order == 2
