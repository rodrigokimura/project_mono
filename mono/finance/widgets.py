"""Finance's widgets"""
from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe


class CategoryWidget(Widget):
    """Dropdown widget with icons"""

    template_name = "widgets/ui_category.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = None

    def get_context(self, name, value, attrs=None):
        return {
            "widget": {
                "name": name,
                "value": value,
            },
            "category_list": self.queryset,
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
