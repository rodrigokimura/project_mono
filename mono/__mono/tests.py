import warnings
from unittest.mock import Mock

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.views.generic.edit import FormView

from .admin import MyAdminSite
from .asgi import application as asgi_app
from .auth_backends import EmailOrUsernameModelBackend
from .context_processors import environment, language_extras
from .decorators import ignore_warnings, stripe_exception_handler
from .mixins import PassRequestToFormViewMixin
from .widgets import (
    ButtonsWidget, CalendarWidget, IconWidget, RadioWidget, SliderWidget,
    ToggleWidget,
)
from .wsgi import application as wsgi_app

User = get_user_model()


class AdminTest(TestCase):

    fixtures = ["icon"]

    @classmethod
    def setUpTestData(cls):
        cls.username = "test_admin"
        cls.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=cls.username)
        user.set_password(cls.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        cls.user = user

    def test_get_app_list(self):
        admin_site = MyAdminSite()

        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = self.user

        app_list = admin_site.get_app_list(request)
        self.assertIsInstance(app_list, list)


class AsgiTest(TestCase):
    def test_asgi_application(self):
        self.assertIsNotNone(asgi_app)


class WsgiTest(TestCase):
    def test_wsgi_application(self):
        self.assertIsNotNone(wsgi_app)


class AuthBackEndsTest(TestCase):

    fixtures = ["icon"]

    @classmethod
    def setUpTestData(cls):
        cls.username = "test_admin"
        cls.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=cls.username)
        user.set_password(cls.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        cls.user = user

    def test_authenticate_method(self):
        authentication_backend = EmailOrUsernameModelBackend()
        factory = RequestFactory()
        request = factory.get('/admin/')
        user = authentication_backend.authenticate(
            request=request,
            username=self.username,
            password=self.password,
        )
        self.assertEqual(user, self.user)
        user = authentication_backend.authenticate(
            request=request,
        )
        self.assertIsNone(user)
        user = authentication_backend.authenticate(
            request=request,
            username=self.username,
            password=User.objects.make_random_password(),
        )
        self.assertIsNone(user)


class ContextProcessorsTest(TestCase):

    def test_environment_method(self):
        factory = RequestFactory()
        request = factory.get('/')
        context = environment(request=request)
        self.assertIn('APP_ENV', context)

    def test_language_extras_method(self):
        factory = RequestFactory()
        request = factory.get('/')
        request.LANGUAGE_CODE = 'pt-br'
        context = language_extras(request=request)
        self.assertIn('LANGUAGE_EXTRAS', context)
        self.assertIn('tinymce_language', context)


class DecoratorsTests(TestCase):

    def test_ignore_warnings(self):
        decorated_func = ignore_warnings(lambda: warnings.warn("test", UserWarning))
        with warnings.catch_warnings(record=True) as w:
            decorated_func()
            self.assertEqual(len(w), 0)

    def test_stripe_exception_handler(self):
        func = Mock(side_effect=stripe.error.CardError("test", "param", "code"))
        decorated_func = stripe_exception_handler(func)
        try:
            decorated_func()
        except (
            stripe.error.CardError,
            stripe.error.RateLimitError,
            stripe.error.InvalidRequestError,
            stripe.error.AuthenticationError,
            stripe.error.APIConnectionError,
            stripe.error.StripeError
        ):
            self.fail('Error was raised')


class MixinTests(TestCase):

    def test_pass_request_to_form_mixin(self):
        class CustomFormView(PassRequestToFormViewMixin, FormView):
            pass

        request = RequestFactory().get('/')
        view = CustomFormView()
        view.setup(request)
        kwargs = view.get_form_kwargs()
        self.assertIn('request', kwargs)


class MockedManager:
    def all(self):
        return [
            {'id': 1, 'name': 'test1'},
            {'id': 2, 'name': 'test2'},
        ]


class MockedModel:
    objects = MockedManager()


class WidgetTests(TestCase):

    def setUp(self) -> None:
        self.choices = [
            (1, "angry"),
            (2, "cry"),
            (3, "slight_frown"),
            (4, "expressionless"),
            (5, "slight_smile"),
            (6, "grinning"),
            (7, "heart_eyes"),
        ]

    def test_calendar_widget_get_context_method(self):
        widget = CalendarWidget()
        context = widget.get_context(name='initial_date', value='1')
        self.assertEqual(context, {
            'widget': {
                'name': 'initial_date',
                'value': '1',
                'placeholder': 'initial date',
            },
            'type': 'datetime',
            'format': 'n/d/Y h:i A',
            'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        })

    def test_calendar_widget_render_method(self):
        widget = CalendarWidget()
        render = widget.render(name='initial_date', value='1')
        self.assertIn('name="initial_date"', str(render))

    def test_toggle_widget_get_context_method(self):
        widget = ToggleWidget()
        context = widget.get_context(name='bool', value='1')
        self.assertEqual(context, {
            'widget': {
                'name': 'bool',
                'value': '1',
            },
        })

    def test_toggle_widget_render_method(self):
        widget = ToggleWidget()
        render = widget.render(name='bool', value='1')
        self.assertIn('name="bool"', str(render))

    def test_radio_widget_get_context_method(self):
        choices = choices = [
            ("R", "Recurrent"),
            ("I", "Installment"),
        ]
        widget = RadioWidget(choices=choices)
        context = widget.get_context(name='radio', value='1')
        self.assertEqual(context, {
            'widget': {
                'name': 'radio',
                'value': '1',
                'choices': choices,
            },
        })

    def test_radio_widget_render_method(self):
        choices = choices = [
            ("R", "Recurrent"),
            ("I", "Installment"),
        ]
        widget = RadioWidget(choices=choices)
        render = widget.render(name='radio', value='1')
        self.assertIn('name="radio"', str(render))

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

    def test_icon_widget_get_context_method(self):
        widget = IconWidget(entity_type=MockedModel)
        context = widget.get_context(name='bool', value='1')
        self.assertEqual(context['widget'], {
            'name': 'bool',
            'value': '1',
        })

    def test_icon_widget_render_method(self):
        widget = IconWidget(entity_type=MockedModel)
        render = widget.render(name='bool', value='1')
        self.assertIn('name="bool"', str(render))
