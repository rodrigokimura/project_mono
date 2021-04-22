from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from .models import Feedback
from .views import FeedbackCreateView


class FeedbackViewTests(TestCase):

    fixtures = ["icon.json"]

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
