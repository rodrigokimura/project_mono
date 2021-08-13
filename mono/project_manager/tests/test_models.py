from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Board, Bucket, Card, Project, card_directory_path, BaseModel


class FunctionTests(TestCase):
    fixtures = ["icon"]

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.project = Project.objects.create(name='test_project', created_by=self.user)
        self.board = Board.objects.create(
            name='test_project',
            created_by=self.user,
            project=self.project,
        )
        self.bucket = Bucket.objects.create(
            name='test_project',
            created_by=self.user,
            board=self.board,
            order=1,
        )

    def test_card_directory_path_function(self):
        card = Card.objects.create(
            name='test',
            created_by=self.user,
            bucket=self.bucket,
            order=1,
        )
        path = card_directory_path(card, 'filename')
        self.assertEqual(path, f'project_{self.project.id}/filename')


class BaseModelTest(TestCase):
    fixtures = ["icon"]

    def setUp(self):
        self.user = User.objects.create(username="test_user")

    def test_str(self):
        project = Project.objects.create(name='test_project', created_by=self.user)
        self.assertEqual(Project.__base__, BaseModel)
        self.assertEqual(str(project), 'test_project')


class ProjectTests(TestCase):
    fixtures = ["icon"]

    def setUp(self):
        self.user_1 = User.objects.create(username="test_user_1")
        self.user_2 = User.objects.create(username="test_user_2")
        self.project = Project.objects.create(name='test_project', created_by=self.user_1)

    def test_allowed_users(self):
        self.assertTrue(self.user_1 in self.project.allowed_users)
        self.assertFalse(self.user_2 in self.project.allowed_users)


class BoardTests(TestCase):
    fixtures = ["icon"]

    def setUp(self):
        self.user_1 = User.objects.create(username="test_user_1")
        self.user_2 = User.objects.create(username="test_user_2")
        self.user_3 = User.objects.create(username="test_user_3")
        self.project = Project.objects.create(name='test_project', created_by=self.user_1)
        self.board = Board.objects.create(
            name='test_project',
            created_by=self.user_1,
            project=self.project,
        )
        self.board.assigned_to.add(self.user_3)
        Bucket.objects.create(
            name='test_project',
            created_by=self.user_1,
            board=self.board,
            order=1,
        )
        Bucket.objects.create(
            name='test_project',
            created_by=self.user_1,
            board=self.board,
            order=2,
        )
        Bucket.objects.create(
            name='test_project',
            created_by=self.user_1,
            board=self.board,
            order=3,
        )

    def test_allowed_users(self):
        self.assertTrue(self.user_1 in self.board.allowed_users)
        self.assertTrue(self.user_3 in self.board.allowed_users)
        self.assertFalse(self.user_2 in self.board.allowed_users)

    def test_max_order(self):
        self.assertEqual(self.board.max_order, 3)


class BucketTests(TestCase):
    fixtures = ["icon"]

    def setUp(self):
        self.user_1 = User.objects.create(username="test_user_1")
        self.project = Project.objects.create(name='test_project', created_by=self.user_1)
        self.board = Board.objects.create(
            name='test_project',
            created_by=self.user_1,
            project=self.project,
        )
        self.bucket_1 = Bucket.objects.create(
            name='test_project',
            created_by=self.user_1,
            board=self.board,
            order=1,
        )
        self.bucket_2 = Bucket.objects.create(
            name='test_project_2',
            created_by=self.user_1,
            board=self.board,
            order=2,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_1,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_1,
            order=2,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_1,
            order=3,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_2,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_2,
            order=1,
        )
        Card.objects.create(
            name='test',
            created_by=self.user_1,
            bucket=self.bucket_2,
            order=1,
        )

    def test_max_order(self):
        self.assertEqual(self.bucket_1.max_order, 3)

    def test_sort(self):
        self.assertEqual(self.bucket_2.max_order, 1)
        self.bucket_2.sort()
        self.assertEqual(self.bucket_2.max_order, 3)

        # class ProjectModelTest(TestCase):
        #     fixtures = ["icon"]

        #     def setUp(self):
        #         self.user = User.objects.create(username="test_user")
        #         Project.objects.create(name='test_project', created_by=self.user)

        #     # def test_name_label(self):
        #     #     project = Project.objects.get(id=1)
        #     #     field_label = project._meta.get_field('name').verbose_name
        #     #     self.assertEqual(field_label, 'name')

        #     # def test_name_max_length(self):
        #     #     project = Project.objects.get(id=1)
        #     #     max_length = project._meta.get_field('name').max_length
        #     #     self.assertEqual(max_length, 50)

        #     # def test_assigned_to_related_name(self):
        #     #     project = Project.objects.get(id=1)
        #     #     related_name = project._meta.get_field('name').related_name
        #     #     self.assertEqual(related_name, 'assigned_projects')

        #     # def test_allowed_users(self):
        #     #     project = Project.objects.get(id=1)
        #     #     allowed_users = project.allowed_users
        #     #     queryset = project.assigned_to.union(User.objects.filter(id=self.created_by.id))
        #     #     self.assertEqual(allowed_users, queryset)

        # class BoardModelTest(TestCase):
        #     fixtures = ["icon"]

        #     def setUp(self):
        #         self.user = User.objects.create(username="test_user")
        #         Board.objects.create(name='test_board', created_by=self.user)

        #     # def test_name_label(self):
        #     #     board = Board.objects.get(id=1)
        #     #     field_label = board._meta.get_field('name').verbose_name
        #     #     self.assertEqual(field_label, 'name')

        #     # def test_name_max_length(self):
        #     #     board = Board.objects.get(id=1)
        #     #     max_length = board._meta.get_field('name').max_length
        #     #     self.assertEqual(max_length, 50)

        #     # def test_assigned_to_related_name(self):
        #     #     board = Board.objects.get(id=1)
        #     #     related_name = board._meta.get_field('name').related_name
        #     #     self.assertEqual(related_name, 'assigned_boards')

        #     # def test_allowed_users(self):
        #     #     board = Board.objects.get(id=1)
        #     #     allowed_users = board.allowed_users
        #     #     queryset = board.assigned_to.union(User.objects.filter(id=self.created_by.id))
        #     #     self.assertEqual(allowed_users, queryset)
