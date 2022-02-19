"""Widgets for the Mono application."""
from dateutil.parser import parse
from django.conf import settings
from django.forms.widgets import Widget
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class CalendarWidget(Widget):
    """Render calendar widget"""
    template_name = 'widgets/ui_calendar.html'
    type = 'datetime'
    format = 'n/d/Y h:i A'

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
        if isinstance(value, str):
            value = parse(value, ignoretz=False)
        template = get_template(self.template_name).render(context)
        return mark_safe(template)


class RadioWidget(Widget):
    """Render a set of radio buttons."""
    template_name = 'widgets/ui_radio.html'

    def __init__(self, attrs=None, **kwargs):
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


class ToggleWidget(Widget):
    """Render toggle widget"""
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
        template = get_template(self.template_name).render(context)
        return mark_safe(template)


class ButtonsWidget(Widget):
    """Render option of grouped buttons"""
    template_name = 'widgets/ui_buttons.html'

    def __init__(self, attrs=None, **kwargs):
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


class IconButtonsWidget(ButtonsWidget):
    """Render option of grouped buttons with icons"""
    template_name = 'widgets/ui_icon_buttons.html'


class SliderWidget(Widget):
    """Render a slider widget"""
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


class IconWidget(Widget):
    """Widget for selecting an icon"""
    template_name = 'widgets/ui_icon.html'

    def __init__(self, entity_type, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.entity_type = entity_type

    def get_context(self, name, value, attrs=None):
        return {
            'widget': {
                'name': name,
                'value': value,
            },
            'icon_list': self.entity_type.objects.all()
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = get_template(self.template_name).render(context)
        return mark_safe(template)
