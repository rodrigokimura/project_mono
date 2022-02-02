"""Curriculum Builder's views"""
from django.views.generic.base import TemplateView

class RootView(TemplateView):
    """
    App's first view.
    """
    template_name = "curriculum_builder/index.html"
