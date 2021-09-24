import time
from typing import Any

import jwt
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files import File
from django.core.files.images import ImageFile
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, UserProfile
from .serializers import ProfileSerializer, UserSerializer


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
        login(request, user, backend='_mono.auth_backends.EmailOrUsernameModelBackend')
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
            # if 'avatar' in request.data:
            #     profile = UserProfile.objects.get_or_create(user=user)
            #     profile.avatar = ImageFile(request.data.get('avatar'))
            #     profile_serializer = ProfileSerializer(profile, data={'avatar': request.data['avatar']})
            #     if profile_serializer.is_valid():
            #         profile.avatar = ImageFile(request.data['avatar'])
            #         profile.save()
            #         pass
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
