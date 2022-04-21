from django.contrib.auth.models import User
from django.test import TestCase
from finance.models import Icon as FinanceIcon

from ..icons import DEFAULT_ICONS
from ..models import (
    BaseModel, Board, Bucket, Card, Icon, Invite, Notification, Project, Theme,
    TimeEntry,
)


class FunctionTests(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
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
        path = Card._card_directory_path(card, 'filename')
        self.assertEqual(path, f'project_{self.project.id}/filename')


class BaseModelTest(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
        self.user = User.objects.create(username="test_user")

    def test_str(self):
        project = Project.objects.create(name='test_project', created_by=self.user)
        self.assertEqual(Project.__base__, BaseModel)
        self.assertEqual(str(project), 'test_project')


class ProjectTests(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
        self.user_1 = User.objects.create(username="test_user_1")
        self.user_2 = User.objects.create(username="test_user_2")
        self.project = Project.objects.create(name='test_project', created_by=self.user_1)

    def test_allowed_users(self):
        self.assertTrue(self.user_1 in self.project.allowed_users)
        self.assertFalse(self.user_2 in self.project.allowed_users)


class BoardTests(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
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

    def setUp(self):
        FinanceIcon.create_defaults()
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


class CardTests(TestCase):

    def setUp(self) -> None:
        FinanceIcon.create_defaults()
        Icon.create_defaults()
        Theme.create_defaults()
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

    def test_start_timer_twice(self):
        response = self.card.start_timer(self.user)
        self.assertEqual(response['action'], 'start')
        response = self.card.start_timer(self.user)
        self.assertEqual(response['action'], 'none')

    def test_stop_timer(self):
        response = self.card.start_timer(self.user)
        self.assertEqual(response['action'], 'start')
        response = self.card.stop_timer()
        self.assertEqual(response['action'], 'stop')


class TimeEntryTests(TestCase):

    def setUp(self) -> None:
        FinanceIcon.create_defaults()
        Icon.create_defaults()
        Theme.create_defaults()
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
        self.time_entry = TimeEntry.objects.create(created_by=self.user, card=self.card)
        self.theme = Theme.objects.first()

    def test_is_running(self):
        self.assertTrue(self.time_entry.is_running)

    def test_is_stopped(self):
        self.assertFalse(self.time_entry.is_stopped)


class ThemeTests(TestCase):

    def setUp(self) -> None:
        FinanceIcon.create_defaults()
        Icon.create_defaults()
        Theme.create_defaults()
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
        self.time_entry = TimeEntry.objects.create(created_by=self.user, card=self.card)
        self.theme = Theme.objects.first()

    def test_theme_name(self):
        self.assertEqual(str(self.theme), 'Red')


class NotificationTests(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
        Icon.create_defaults()
        Theme.create_defaults()
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.notification: Notification = Notification.objects.create(
            title='test',
            message='message',
            to=self.user,
        )

    def test_str(self):
        self.assertEqual(str(self.notification), 'test')

    def test_read(self):
        self.assertFalse(self.notification.read)

    def test_mark_as_read(self):
        self.notification.mark_as_read()
        self.assertIsNotNone(self.notification.read_at)

    def test_mark_as_unread(self):
        self.notification.mark_as_unread()
        self.assertIsNone(self.notification.read_at)


class CreateDefaultsTest(TestCase):

    def test_create_default_themes(self):
        Theme.create_defaults()
        for theme in Theme.DEFAULT_THEMES:
            name = theme[0]
            self.assertTrue(Theme.objects.filter(name=name).exists())

    def test_create_default_icons(self):
        Icon.create_defaults()
        for icon in DEFAULT_ICONS:
            self.assertTrue(Icon.objects.filter(markup=icon).exists())


class InviteTests(TestCase):

    def setUp(self):
        FinanceIcon.create_defaults()
        Icon.create_defaults()
        Theme.create_defaults()
        self.user = User.objects.create_user(username="test", email="test@test.com", password="supersecret")
        self.project = Project.objects.create(name='test', created_by=self.user)
        self.invite = Invite.objects.create(
            email='test2@test.com',
            project=self.project,
        )

    def test_str(self):
        self.assertIsNotNone(str(self.invite))
