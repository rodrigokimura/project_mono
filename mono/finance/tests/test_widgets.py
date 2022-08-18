from django.test import TestCase

from ..models import Category
from ..widgets import CategoryWidget


class WidgetTests(TestCase):
    def setUp(self) -> None:
        self.choices = Category._meta.get_field("type").get_choices()

    def test_category_widget_get_context_method(self):
        widget = CategoryWidget()
        widget.queryset = None
        context = widget.get_context(name="bool", value="1")
        self.assertEqual(
            context["widget"],
            {
                "name": "bool",
                "value": "1",
            },
        )

    def test_category_widget_render_method(self):
        widget = CategoryWidget()
        widget.queryset = None
        render = widget.render(name="bool", value="1")
        self.assertIn('name="bool"', str(render))
