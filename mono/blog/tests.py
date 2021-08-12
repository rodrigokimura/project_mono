from django.test import TestCase
from django.test.client import Client
from .models import Post, User


class BlogViewTests(TestCase):

    fixtures = ['icon']

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test.test@test.com",
        )
        self.user.set_password('supersecret')
        self.user.is_staff = True
        self.user.save()

    def test_post_create_view(self):
        c = Client()
        c.login(username=self.user.username, password='supersecret')
        c.post(
            '/bl/post/',
            {
                'title': 'TEST',
                'content': '<h1>TEST</h1>',
                'author': self.user.id,
            }
        )
        self.assertEqual(Post.objects.last().title, 'TEST')

    def test_post_update_view(self):
        post = Post.objects.create(
            title="TEST2",
            content="<h2>Test</h2>",
            author=self.user,
        )
        c = Client()
        c.login(username=self.user.username, password='supersecret')
        c.post(
            f'/bl/post/{post.id}/',
            {
                'title': 'TEST2-changed',
                'content': '<h2>Test-changed</h2>',
                'author': self.user.id,
            }
        )
        self.assertEqual(Post.objects.get(id=post.id).title, 'TEST2-changed')

    def test_post_delete_view(self):
        post = Post.objects.create(
            title="TEST3",
            content="<h2>Test</h2>",
            author=self.user,
        )
        c = Client()
        c.login(username=self.user.username, password='supersecret')
        c.post(
            f'/bl/post/{post.id}/delete/',
        )
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_post_list_view(self):
        c = Client()
        c.login(username=self.user.username, password='supersecret')
        r = c.get('/bl/posts/')
        self.assertEqual(r.status_code, 200)
