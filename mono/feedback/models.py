"""Feedback's models"""
from accounts.models import Notification, User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Feedback(models.Model):
    """Feedback given from any user."""

    FEELING_CHOICES = [
        (1, "angry"),
        (2, "cry"),
        (3, "slight_frown"),
        (4, "expressionless"),
        (5, "slight_smile"),
        (6, "grinning"),
        (7, "heart_eyes"),
    ]

    user = models.ForeignKey(get_user_model(), verbose_name=_("user"), on_delete=models.SET_NULL, null=True)
    feeling = models.IntegerField(_("feeling"), choices=FEELING_CHOICES)
    message = models.TextField(_("message"), max_length=1000)
    public = models.BooleanField(_("public"), default=False)

    def notify_admins(self):
        """
        Send email notification to admins
        """

        template_html = 'email/alert.html'
        template_text = 'email/alert.txt'

        text = get_template(template_text)
        html = get_template(template_html)

        site = settings.SITE

        full_link = site + reverse('admin:feedback_feedback_change', args=[self.id])

        context = {
            'warning_message': 'Feedback received',
            'first_line': f'Feedback received: {self.message}',
            'button_text': 'View feedback',
            'button_link': full_link,
        }
        mail_admins(
            subject='Feedback',
            message=text.render(context),
            html_message=html.render(context),
        )
        for user in User.objects.filter(is_superuser=True):
            Notification.objects.create(
                title="Feedback received",
                message="A feedback has just been received.",
                icon='exclamation',
                to=user,
                action_url=full_link,
            )
