from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls.base import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Project, Board
from .forms import ProjectForm, BoardForm
from .mixins import PassRequestToFormViewMixin


class ProjectListView(ListView):
    model = Project
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Projects', None),
        ]
        return context


class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: view', None),
        ]
        return context


class ProjectCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: create', None),
        ]
        return context


class ProjectUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Project: edit', None),
        ]
        return context


class ProjectDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('project_manager:projects')
    success_message = "Project was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)


class BoardListView(ListView):
    model = Board
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Boards', None),
        ]
        return context


class BoardDetailView(DetailView):
    model = Board

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            (f'Project: {self.object}', reverse('project_manager:project_detail', args=[self.object.id])),
            ('Board: view', None),
        ]
        return context


class BoardCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Board: create', None),
        ]
        return context


class BoardUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Board
    form_class = BoardForm
    success_url = reverse_lazy('project_manager:boards')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('Project Manager', reverse('project_manager:projects')),
            ('Board: edit', None),
        ]
        return context


class BoardDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Board
    success_url = reverse_lazy('project_manager:boards')
    success_message = "Board was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)
