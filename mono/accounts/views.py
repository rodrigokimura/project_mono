from django.contrib.auth import views
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render

from . import forms


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/signup.html"


def sign_up(request):
    template = "accounts/signup.html"
    if request.method == "POST":
        uform = forms.UserCreateForm(data=request.POST)
        pform = forms.UserProfileForm(data=request.POST, files=request.FILES)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()
            profile = pform.save(commit=False)
            profile.user = user
            profile.save()
        else:
            for field in uform.errors:
                uform[field].field.widget.attrs.update({'class': 'field error'})
            for field in pform.errors:
                pform[field].field.widget.attrs.update({'class': 'field error'})
    elif request.method == "GET":
        uform = forms.UserCreateForm()
        pform = forms.UserProfileForm()

    return render(request, template, {
        "uform": uform,
        "pform": pform
    })


class Login(views.LoginView):
    template_name = "accounts/login.html"
    success_url = reverse_lazy("homepage:home")


class Logout(views.LogoutView):
    next_page = "/"


class PasswordChange(views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:password_change_done")


class PasswordChangeDone(views.PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
    extra_context = {"mensagem": "Senha alterada com sucesso!"}


class PasswordReset(views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    html_email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    form_class = forms.CustomPasswordResetForm


class PasswordResetDone(views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"
    extra_context = {"mensagem": "O link para redefinição de senha foi enviado ao email cadastrado!"}


class PasswordResetConfirm(views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    post_reset_login = True
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetComplete(views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
    extra_context = {"mensagem": "A senha foi redefinida com sucesso!"}
