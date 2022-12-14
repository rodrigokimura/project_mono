"""Typer views"""
from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from .models import Lesson


class IndexView(LoginRequiredMixin, TemplateView):
    """Main view for Typer app"""

    template_name = "typer/index.html"


class LessonListView(LoginRequiredMixin, TemplateView):
    """List view for Typer app"""

    template_name = "typer/lesson_list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        lessons = Lesson.objects.filter(
            Q(created_by=self.request.user) | Q(created_by__isnull=True)
        )
        context["lessons"] = lessons
        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    """Detail view for Typer app"""

    template_name = "typer/detail.html"
    model = Lesson
