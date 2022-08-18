"""Feedback's views"""
from __mono.mixins import PassRequestToFormViewMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from .forms import FeedbackForm
from .models import Feedback


class FeedbackCreateView(
    PassRequestToFormViewMixin, SuccessMessageMixin, CreateView
):
    """Create feedback"""

    model = Feedback
    form_class = FeedbackForm
    success_url = reverse_lazy("home")
    success_message = _("Your feedback was sent! Thank you!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feelings"] = Feedback.FEELING_CHOICES
        return context
