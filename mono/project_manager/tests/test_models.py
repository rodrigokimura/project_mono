from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Board, Project


class ProjectModelTest(TestCase):
    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        Project.objects.create(name='test_project', created_by=self.user)

    # def test_name_label(self):
    #     project = Project.objects.get(id=1)
    #     field_label = project._meta.get_field('name').verbose_name
    #     self.assertEqual(field_label, 'name')

    # def test_name_max_length(self):
    #     project = Project.objects.get(id=1)
    #     max_length = project._meta.get_field('name').max_length
    #     self.assertEqual(max_length, 50)

    # def test_assigned_to_related_name(self):
    #     project = Project.objects.get(id=1)
    #     related_name = project._meta.get_field('name').related_name
    #     self.assertEqual(related_name, 'assigned_projects')

    # def test_allowed_users(self):
    #     project = Project.objects.get(id=1)
    #     allowed_users = project.allowed_users
    #     queryset = project.assigned_to.union(User.objects.filter(id=self.created_by.id))
    #     self.assertEqual(allowed_users, queryset)


class BoardModelTest(TestCase):
    fixtures = ["icon.json"]

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        Board.objects.create(name='test_board', created_by=self.user)

    # def test_name_label(self):
    #     board = Board.objects.get(id=1)
    #     field_label = board._meta.get_field('name').verbose_name
    #     self.assertEqual(field_label, 'name')

    # def test_name_max_length(self):
    #     board = Board.objects.get(id=1)
    #     max_length = board._meta.get_field('name').max_length
    #     self.assertEqual(max_length, 50)

    # def test_assigned_to_related_name(self):
    #     board = Board.objects.get(id=1)
    #     related_name = board._meta.get_field('name').related_name
    #     self.assertEqual(related_name, 'assigned_boards')

    # def test_allowed_users(self):
    #     board = Board.objects.get(id=1)
    #     allowed_users = board.allowed_users
    #     queryset = board.assigned_to.union(User.objects.filter(id=self.created_by.id))
    #     self.assertEqual(allowed_users, queryset)
