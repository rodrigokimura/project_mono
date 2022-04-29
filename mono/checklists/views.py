"""Todo Lists' views"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


class HomePageView(LoginRequiredMixin, TemplateView):
    """
    Root view
    """

    template_name = "checklists/home.html"
