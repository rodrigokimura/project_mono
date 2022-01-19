import json
import time
from typing import Any

import jwt
import stripe
from django import http
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetCompleteView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import BadRequest, PermissionDenied
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import UserForm
from .mixins import PassRequestToFormViewMixin
from .models import Notification, User, UserProfile
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
        count = unread_notifications.count()
        if count > 0:
            messages.add_message(
                self.request,
                messages.WARNING,
                f'You have {unread_notifications.count()} unread notification{"s" if count > 1 else ""}.',
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

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            customer = stripe.Customer.list(email=self.request.user.email).data[0]
            payment_method = stripe.PaymentMethod.retrieve(customer.invoice_settings.default_payment_method)
            context['payment_method'] = payment_method
        except IndexError:
            context['payment_method'] = None

        notifications = self.request.user.notifications
        context['notifications'] = {
            'unread': notifications.filter(read_at__isnull=True).order_by('-created_at'),
            'read': notifications.filter(read_at__isnull=False).order_by('-created_at'),
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
        if request.user == user:
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('You are trying to edit another user.', status=status.HTTP_403_FORBIDDEN)


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


class NotificationCountView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        qs = self.request.user.notifications.filter(
            read_at__isnull=True
        )
        if qs.exists():
            count = qs.count()
            timestamp = qs.last().created_at.isoformat()
        else:
            count = 0
            timestamp = None
        return JsonResponse({
            'success': True,
            'count': count,
            'timestamp': timestamp,
        })


class NotificationActionView(LoginRequiredMixin, SingleObjectMixin, View):

    model = Notification

    def get(self, *args, **kwargs):

        notification = self.get_object()
        if not notification.to == self.request.user:
            raise PermissionDenied
        if not notification.read:
            notification.mark_as_read()
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Notification marked as read.',
            )
        if notification.action_url:
            return redirect(notification.action_url)
        return redirect('/')


class MarkNotificationsAsReadView(LoginRequiredMixin, View):

    def post(self, request):
        ids = json.loads(request.POST.get('ids', ''))

        if len(ids) == 0:
            raise BadRequest('No notification ids were passed.')

        for id in ids:
            n = Notification.objects.get(id=int(id))
            if n.to == request.user:
                n.mark_as_read()

        messages.add_message(
            request,
            messages.SUCCESS,
            f'You marked {len(ids)} notification{"s" if len(ids) > 1 else ""} as read.',
        )
        return JsonResponse({
            'success': True,
            'data': ids
        })


class MarkNotificationsAsUnreadView(LoginRequiredMixin, View):

    def post(self, request):
        ids = json.loads(request.POST.get('ids', ''))
        for id in ids:
            n = Notification.objects.get(id=int(id))
            if n.to == request.user:
                n.mark_as_unread()
        messages.add_message(
            request,
            messages.SUCCESS,
            f'You marked {len(ids)} notification{"s" if len(ids) > 1 else ""} as unread.',
        )
        return JsonResponse({
            'success': True,
            'data': ids
        })


class ApiMeView(RetrieveAPIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class ApiLogoutView(APIView):

    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response(
            {
                "success": True,
                "message": "Token was successfully deleted.",
            }
        )
