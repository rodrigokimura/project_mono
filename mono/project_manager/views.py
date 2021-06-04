from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls.base import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Project
from .forms import ProjectForm
from .mixins import PassRequestToFormViewMixin


class ProjectListView(ListView):
    model = Project
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

class ProjectDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


# class GroupListView(LoginRequiredMixin, ListView):
#     model = Group

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         groups = Group.objects.filter(members=self.request.user)
#         members = [m.id for g in groups for m in g.members.all()]
#         context['members'] = User.objects.filter(id__in=members).exclude(id=self.request.user.id)
#         return context

#     def get_queryset(self):
#         qs = Group.objects.filter(members=self.request.user)

#         member = self.request.GET.get('member', None)
#         if member not in [None, ""]:
#             qs = qs.filter(members=member)

#         return qs


class ProjectCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was created successfully"


class ProjectUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('project_manager:projects')
    success_message = "%(name)s was updated successfully"


class ProjectDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('project_manager:projects')
    success_message = "Project was deleted successfully"

    def test_func(self):
        return self.get_object().owned_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ProjectDeleteView, self).delete(request, *args, **kwargs)
