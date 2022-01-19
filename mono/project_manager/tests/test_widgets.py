from django.test import TestCase

from ..widgets import IconWidget


class WidgetTests(TestCase):

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
