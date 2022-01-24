"""Accounts' forms"""
from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import (
    authenticate, forms as auth_forms, get_user_model, login,
)
from django.forms import ValidationError
from django.utils.translation import gettext as _

from . import models


class UserForm(auth_forms.UserCreationForm):
    """User form"""

    error_css_class = 'error'

    captcha = ReCaptchaField()
    email = forms.EmailField()

    class Meta:
        fields = ("username", "email", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': self.fields["username"].label})
        self.fields['email'].widget.attrs.update({'placeholder': _("Email")})
        self.fields['password1'].widget.attrs.update({'placeholder': self.fields["password1"].label})
        self.fields['password2'].widget.attrs.update({'placeholder': self.fields["password2"].label})
        self.fields['captcha'].widget.api_params = {'hl': self.request.LANGUAGE_CODE}

    def clean(self):
        email = self.cleaned_data.get('email')
        if models.User.objects.filter(email=email).exists():
            raise ValidationError(_("Email already exists. Please use another one."))
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            auth_user = authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password1']
            )
            login(self.request, auth_user)
        return user


class UserProfileForm(forms.ModelForm):
    """User profile form"""
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'placeholder': 'Avatar'})

    class Meta:
        model = models.UserProfile
        fields = [
            "avatar",
        ]
