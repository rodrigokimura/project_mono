from django.contrib.auth import login
from .models import User, UserProfile
from django.conf import settings
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
import jwt
import time


class AccountVerificationView(TemplateView):
    template_name = "finance/invite_acceptance.html"

    def get(self, request):
        token = request.GET.get('t', None)

        if token is None:
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
