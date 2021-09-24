from django.conf import settings
from django.test import RequestFactory, TestCase
from django.views.generic.edit import FormView

from .mixins import PassRequestToFormViewMixin
from .widgets import CalendarWidget, CategoryWidget, ToggleWidget


class WidgetTests(TestCase):

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

    def test_category_widget_get_context_method(self):
        widget = CategoryWidget()
        widget.queryset = None
        context = widget.get_context(name='bool', value='1')
        self.assertEqual(context['widget'], {
            'name': 'bool',
            'value': '1',
        })

    def test_category_widget_render_method(self):
        widget = CategoryWidget()
        widget.queryset = None
        render = widget.render(name='bool', value='1')
        self.assertIn('name="bool"', str(render))


class MixinTests(TestCase):
    def test_pass_request_to_form_mixin(self):
        class CustomFormView(PassRequestToFormViewMixin, FormView):
            pass

        request = RequestFactory().get('/')
        view = CustomFormView()
        view.setup(request)
        kwargs = view.get_form_kwargs()
        self.assertIn('request', kwargs)
