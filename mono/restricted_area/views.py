"""Restricted area's views"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView, View

from .report import Report


class IndexView(UserPassesTestMixin, TemplateView):
    """
    Root view
    """

    template_name = 'restricted_area/index.html'

    def test_func(self):
        return self.request.user.is_superuser


class ForceError500View(UserPassesTestMixin, View):
    """Simulate error"""

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        raise Exception("Faking an error.")


class ViewError500View(UserPassesTestMixin, TemplateView):
    """Display error page"""

    template_name = '500.html'

    def test_func(self):
        return self.request.user.is_superuser


class ReportView(UserPassesTestMixin, TemplateView):
    """Show report of models"""

    template_name = 'restricted_area/report.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['models'] = Report().get_models()
        return context
