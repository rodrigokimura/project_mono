import time
from typing import Any

import jwt
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetView,
)
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserForm
from .mixins import PassRequestToFormViewMixin
from .models import User, UserProfile
from .serializers import ProfileSerializer, UserSerializer


class SignUp(SuccessMessageMixin, PassRequestToFormViewMixin, CreateView):
    form_class = UserForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('home')
    success_message = "%(username)s user created successfully"


class Login(LoginView):
    template_name = "accounts/login.html"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        unread_notifications = self.request.user.notifications.filter(
            read_at__isnull=True
        )
        if unread_notifications.count() > 0:
            messages.add_message(
                self.request, 
                messages.WARNING, 
                f'You have {unread_notifications.count()} unread notification(s).',
            )
        return response


class Logout(LogoutView):
    next_page = reverse_lazy('home')


class PasswordResetView(PasswordResetView):
    success_url = reverse_lazy('finance:password_reset_done')
    title = _('Password reset')
    html_email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    template_name = 'registration/password_reset_form.html'
    extra_email_context = {
        "expiration_time_hours": int(settings.PASSWORD_RESET_TIMEOUT / 60 / 60)
    }


class PasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('finance:password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'
    title = _('Enter new password')


class PasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
    title = _('Password reset complete')


class AccountVerificationView(TemplateView):
    template_name = "finance/invite_acceptance.html"

    def get(self, request):
        token = request.GET.get('t', None)

        if token is None or token == '':
            return HttpResponse("error")

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        user = get_object_or_404(User, pk=payload['user_id'])
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.verify()
        return self.render_to_response({
            "accepted": True,
        })


class LoginAsView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request):
        time.sleep(2)
        user = get_object_or_404(User, id=request.POST.get('user'))
        login(request, user, backend='__mono.auth_backends.EmailOrUsernameModelBackend')
        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully logged in as {user.username}",
            }
        )


class ConfigView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/config.html"

    def get(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        up: UserProfile = self.request.user.profile
        if not up.avatar:
            up.generate_initials_avatar()
        context = super().get_context_data(**kwargs)
        notifications = self.request.user.notifications
        context['notifications'] = {
            'unread': notifications.filter(read_at__isnull=True),
            'read': notifications.filter(read_at__isnull=False),
        }
        return context


class UserDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None, **kwargs):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if request.user == user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)


class UserProfileDetailAPIView(LoginRequiredMixin, APIView):
    """
    Retrieve or update a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None, **kwargs):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if request.user == profile.user:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('User not allowed', status=status.HTTP_403_FORBIDDEN)
