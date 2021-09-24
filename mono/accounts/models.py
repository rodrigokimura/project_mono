from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.fields import DateTimeField
from django.template.loader import get_template
from django.urls.base import reverse
from django.utils import timezone
from finance.models import Icon, Notification

User = get_user_model()


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        default=None,
    )
    verified_at = DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.user)

    def verify(self):
        self.verified_at = timezone.now()
        self.save()
        Notification.objects.create(
            title="Account verification",
            message="Your account was successfully verified.",
            icon=Icon.objects.get(markup="exclamation"),
            to=self.user
        )

    def send_verification_email(self):

        token = jwt.encode(
            {
                "exp": timezone.now() + timedelta(days=30),
                "user_id": self.user.id
            },
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        template_html = 'email/alert.html'
        template_text = 'email/alert.txt'

        text = get_template(template_text)
        html = get_template(template_html)

        site = settings.SITE

        full_link = site + f"{reverse('accounts:verify')}?t={token}"

        d = {
            'warning_message': 'Account verification',
            'first_line': 'We need to verify your account. Please click the button below.',
            'button_text': 'Verify',
            'button_link': full_link,
        }

        msg = EmailMultiAlternatives(
            subject='Invite',
            body=text.render(d),
            from_email=settings.EMAIL_HOST_USER,
            to=[self.user.email])
        msg.attach_alternative(html.render(d), "text/html")
        msg.send(fail_silently=False)

        Notification.objects.create(
            title="Account verification",
            message="We've sent you an email to verify your account.",
            icon=Icon.objects.get(markup="exclamation"),
            to=self.user,
        )
