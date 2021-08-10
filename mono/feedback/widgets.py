from django.forms.widgets import Widget
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class ButtonsWidget(Widget):
    template_name = 'widgets/ui_icon_buttons.html'

    def __init__(self, attrs=None, *args, **kwargs):
        self.choices = kwargs.pop('choices')
        super().__init__(attrs)

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
                'choices': self.choices,
            },
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = get_template(self.template_name).render(context)
        return mark_safe(template)


class SliderWidget(Widget):
    template_name = 'widgets/ui_slider.html'

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
                'label': _(name).title(),
            },
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = get_template(self.template_name).render(context)
        return mark_safe(template)
