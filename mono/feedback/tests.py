from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.test.client import Client

from .models import Feedback
from .views import FeedbackCreateView


class FeedbackViewTests(TestCase):

    fixtures = ["icon"]

    def setUp(self):
        self.user = User.objects.create(username="User")
        self.feedback = Feedback.objects.create(
            user=self.user,
            feeling=1,
            message="Message",
            public=False,
        )
        self.assertIsNotNone(self.user)
        self.factory = RequestFactory()

    def test_feedback_creation(self):
        self.assertIsNotNone(self.feedback)

    def test_feedback_view(self):
        request = self.factory.get('/fb/')
        request.user = self.user

        response = FeedbackCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        c = Client()
        c.force_login(self.user)
        c.post('/fb/', {
            'user': self.user,
            'feeling': 1,
            'message': "I'm angry",
        })
        self.assertTrue(Feedback.objects.filter(message="I'm angry").exists())
