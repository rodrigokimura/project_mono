"""Mind maps views"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.base import TemplateView


class IndexView(UserPassesTestMixin, TemplateView):

    template_name = "mind_maps/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
