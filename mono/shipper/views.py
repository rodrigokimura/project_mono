"""Shipper's views"""
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .forms import ShipForm
from .models import Ship


class ShipView(TemplateView):
    """Root view"""

    template_name = "shipper/index.html"

    def get_context_data(self, **kwargs):
        """Add extra context"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Shipper"
        context["description"] = "A simple couple name generator"
        return context


class ShipDetailView(DetailView):
    model = Ship


class ShipCreateView(CreateView):
    """Create ship"""

    model = Ship
    form_class = ShipForm

    def get_success_url(self):
        return reverse("shipper:ship_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        return kwargs
