"""Mind maps views"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .models import MindMap


class IndexView(UserPassesTestMixin, TemplateView):

    template_name = "mind_maps/index.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        mind_maps = MindMap.objects.filter(created_by=self.request.user)
        context = super().get_context_data(**kwargs)
        context["mind_maps"] = mind_maps
        return context


class MindMapDetailView(UserPassesTestMixin, TemplateView):

    template_name = "mind_maps/index.html"
    model = MindMap

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PlaygroundView(UserPassesTestMixin, DetailView):

    template_name = "mind_maps/playground.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
