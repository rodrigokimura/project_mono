from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from .models import Post
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib import messages


class PostCreateView(UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:posts')
    success_message = "%(title)s was created successfully"

    def test_func(self):
        return self.request.user.is_staff


class PostUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('blog:posts')
    success_message = "%(title)s was updated successfully"

    def test_func(self):
        return self.request.user.is_staff


class PostDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:posts')
    success_message = "Post was deleted successfully"

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class PostListView(UserPassesTestMixin, ListView):
    model = Post

    def test_func(self):
        return self.request.user.is_staff
