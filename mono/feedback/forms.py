"""Feedback's forms"""
from __mono.widgets import IconButtonsWidget, SliderWidget
from django import forms
from django.utils.translation import gettext as _

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    """Feedback form"""
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
        if self.request.user.is_authenticated:
            feedback.user = self.request.user
            feedback.save()
        return super().save(*args, **kwargs)

    class Meta:
        model = Feedback
        fields = ['feeling', 'message', 'public']
        widgets = {
            'feeling': IconButtonsWidget(choices=Feedback.FEELING_CHOICES),
            'public': SliderWidget,
        }
        error_messages = {
            'feeling': {
                'invalid_choice': _("Please, select a valid option.")
            }
        }
