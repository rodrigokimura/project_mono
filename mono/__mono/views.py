"""Class-based views for the mono app."""
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import DeleteView


class ProtectedDeleteView(UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Class-based view for deleting an object."""

    def test_func(self):
        return self.get_object().created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
