from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.test.client import Client
from .models import Feedback
from .views import FeedbackCreateView
from .widgets import ButtonsWidget, SliderWidget


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

        c = Client()
        c.force_login(self.user)
        c.post('/fb/', {
            'user': self.user,
            'feeling': 1,
            'message': "I'm angry",
        })
        self.assertTrue(Feedback.objects.filter(message="I'm angry").exists())


class FeedbackWidgetTests(TestCase):

    def setUp(self) -> None:
        self.choices = Feedback._meta.get_field('feeling').get_choices()

    def test_buttons_widget_get_context_method(self):
        buttons_widget = ButtonsWidget(choices=self.choices)
        context = buttons_widget.get_context(name='feeling', value='1')
        self.assertEqual(context, {
            'widget': {
                'name': 'feeling',
                'value': '1',
                'choices': self.choices,
            },
        })

    def test_buttons_widget_render_method(self):
        buttons_widget = ButtonsWidget(choices=self.choices)
        render = buttons_widget.render(name='feeling', value='1')
        self.assertIn('name="feeling"', str(render))

    def test_slider_widget_get_context_method(self):
        slider_widget = SliderWidget()
        context = slider_widget.get_context(name='public', value=True)
        self.assertEqual(context, {
            'widget': {
                'name': 'public',
                'value': True,
                'label': 'Public',
            },
        })

    def test_slider_widget_render_method(self):
        slider_widget = SliderWidget()
        render = slider_widget.render(name='public', value=True)
        self.assertIn('name="public"', str(render))
