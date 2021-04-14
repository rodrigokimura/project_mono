from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


class Feedback(models.Model):

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
