"""Restricted area's views"""
from functools import reduce

from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View

from .report import Report


class IndexView(UserPassesTestMixin, TemplateView):
    """
    Root view
    """

    template_name = "restricted_area/index.html"

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

    template_name = "500.html"

    def test_func(self):
        return self.request.user.is_superuser


class ReportView(UserPassesTestMixin, TemplateView):
    """Show report of models"""

    template_name = "restricted_area/report.html"

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["models"] = Report().get_models()
        return context


class LoginAsView(UserPassesTestMixin, View):
    """
    Sign in as another user.
    """

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        """
        Search users
        """
        query = request.GET.get("query")
        fields_to_search = ["username", "email", "first_name", "last_name"]
        users = get_user_model().objects.filter(
            reduce(
                lambda x, y: x | y,
                (Q(**{f"{f}__icontains": query}) for f in fields_to_search),
            )
        )
        return JsonResponse(
            {
                "success": True,
                "results": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "profile_picture": user.profile.avatar.url
                        if user.profile.avatar
                        else None,
                    }
                    for user in users
                ],
            }
        )

    def post(self, request):
        """
        Sign in as another user.
        """
        user = get_object_or_404(get_user_model(), id=request.POST.get("user"))
        login(
            request,
            user,
            backend="__mono.auth_backends.EmailOrUsernameModelBackend",
        )
        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully logged in as {user.username}",
            }
        )
