from django.conf import settings
from django.test import TestCase

from ..models import Category
from ..widgets import (
    ButtonsWidget, CalendarWidget, CategoryWidget, IconWidget, RadioWidget,
    ToggleWidget,
)


class WidgetTests(TestCase):

    def setUp(self) -> None:
        self.choices = Category._meta.get_field('type').get_choices()

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

    def test_icon_widget_get_context_method(self):
        widget = IconWidget()
        context = widget.get_context(name='bool', value='1')
        self.assertEqual(context['widget'], {
            'name': 'bool',
            'value': '1',
        })

    def test_icon_widget_render_method(self):
        widget = IconWidget()
        render = widget.render(name='bool', value='1')
        self.assertIn('name="bool"', str(render))
