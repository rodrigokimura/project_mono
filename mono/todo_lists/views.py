from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls.base import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import List, Item
from .forms import ListForm, ItemForm
from .mixins import PassRequestToFormViewMixin


class ListListView(ListView):
    model = List
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('Lists', None),
        ]
        return context


class ListDetailView(DetailView):
    model = List

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('List: view', None),
        ]
        return context


class ListCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('List: create', None),
        ]
        return context


class ListUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = List
    form_class = ListForm
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('List: edit', None),
        ]
        return context


class ListDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = List
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "List was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class ItemListView(ListView):
    model = Item
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('Items', None),
        ]
        return context


class ItemDetailView(DetailView):
    model = Item

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            (f'Project: {self.object}', reverse('todo_lists:project_detail', args=[self.object.id])),
            ('Item: view', None),
        ]
        return context


class ItemCreateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "%(name)s was created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('Item: create', None),
        ]
        return context


class ItemUpdateView(LoginRequiredMixin, PassRequestToFormViewMixin, SuccessMessageMixin, UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = [
            ('Home', reverse('home')),
            ('To-do Lists', reverse('todo_lists:lists')),
            ('Item: edit', None),
        ]
        return context


class ItemDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('todo_lists:lists')
    success_message = "Item was deleted successfully"

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
