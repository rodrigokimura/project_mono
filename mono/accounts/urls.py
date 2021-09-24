from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("verify", views.AccountVerificationView.as_view(), name='verify'),
    path("login-as", views.LoginAsView.as_view(), name='login_as'),
]
