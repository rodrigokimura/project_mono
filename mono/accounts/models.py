from django.contrib import auth
from django.db import models
from django.utils import timezone
from django.utils.functional import empty
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=256, blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=(('m', 'Masculino'), ('f', 'Feminino'), ('n', 'Não informar')),
        blank=True, null=True)

    avatar = models.ImageField(null=True)

    def __str__(self):
        return str(self.user)