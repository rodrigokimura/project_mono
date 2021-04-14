from django import forms
from .models import Feedback
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
                'label': name.title(),
            },
        }

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = get_template(self.template_name).render(context)
        return mark_safe(template)


class FeedbackForm(forms.ModelForm):
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update(
            {
                'placeholder': _('Please, tell us what is on your mind.')
            }
        )

    def save(self, *args, **kwargs):
        feedback = self.instance
        feedback.user = self.request.user
        feedback.save()
        return super().save(*args, **kwargs)

    class Meta:
        model = Feedback
        fields = ['feeling', 'message', 'public']
        widgets = {
            'feeling': ButtonsWidget(choices=Feedback.FEELING_CHOICES),
            'public': SliderWidget,
        }
        error_messages = {
            'feeling': {
                'invalid_choice': _("Please, select a valid option.")
            }
        }
