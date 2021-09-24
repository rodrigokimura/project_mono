from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.edit import CreateView

from .forms import FeedbackForm
from .models import Feedback


class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class FeedbackCreateView(PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_url = reverse_lazy('home')
    success_message = _("Your feedback was sent! Thank you!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feelings"] = Feedback.FEELING_CHOICES
        return context
