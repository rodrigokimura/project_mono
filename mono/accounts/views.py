from mono.accounts.models import User, UserProfile
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import jwt


class AccountVerificationView(LoginRequiredMixin, TemplateView):
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
        if request.user == user:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.verify()
        return self.render_to_response({
            "accepted": True,
        })
