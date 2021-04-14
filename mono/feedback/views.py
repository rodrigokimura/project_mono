from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from .models import Feedback
from .forms import FeedbackForm


class PassRequestToFormViewMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class FeedbackCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_url = reverse_lazy('finance:index')
    success_message = _("Your feedback was sent! Thank you!")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feelings"] = Feedback.FEELING_CHOICES
        return context
