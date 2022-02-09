"""Curriculum Builder's views"""
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Curriculum


class RootView(TemplateView):
    """
    App's first view.
    """
    template_name = "curriculum_builder/index.html"


class CurriculumListView(ListView):
    """
    List of user's curricula.
    """
    model = Curriculum
    paginate_by = 20
    template_name = 'curriculum_builder/curriculum_list.html'

    def get_queryset(self):
        return Curriculum.objects.filter(created_by=self.request.user)


class CurriculumDetailView(DetailView):
    """
    Curriculum detail view.
    """
    model = Curriculum
    template_name = 'curriculum_builder/curriculum_detail.html'


class CurriculumEditView(DetailView):
    """
    Curriculum edit view.
    """
    model = Curriculum
    template_name = 'curriculum_builder/curriculum_edit.html'
