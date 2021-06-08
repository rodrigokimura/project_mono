from django.forms.widgets import Widget
from django.template import loader
from django.utils.safestring import mark_safe
from django.conf import settings
from dateutil.parser import parse
from .models import Icon


class CalendarWidget(Widget):
    template_name = 'widgets/ui_calendar.html'
    type = 'datetime'
    format = 'n/d/Y h:i A'

    def __init__(self, attrs=None, *args, **kwargs):
        super().__init__(attrs)

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
                'placeholder': name.replace('_', ' '),
            },
            'type': self.type,
            'format': self.format,
            'LANGUAGE_EXTRAS': settings.LANGUAGE_EXTRAS,
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        if type(value) == str:
            value = parse(value, ignoretz=False)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class IconWidget(Widget):
    template_name = 'widgets/ui_icon.html'

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
            'icon_list': Icon.objects.all()
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class ButtonsWidget(Widget):
    template_name = 'widgets/ui_buttons.html'

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
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class RadioWidget(Widget):
    template_name = 'widgets/ui_radio.html'

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
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class CategoryWidget(Widget):
    template_name = 'widgets/ui_category.html'

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
            'category_list': self.queryset
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)


class ToggleWidget(Widget):
    template_name = 'widgets/ui_toggle.html'

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
