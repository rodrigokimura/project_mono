from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("verify/", views.AccountVerificationView.as_view(), name='verify'),
    path("login-as/", views.LoginAsView.as_view(), name='login_as'),
    path("config/", views.ConfigView.as_view(), name='config'),
    path("users/<int:pk>/", views.UserDetailAPIView.as_view(), name='user_detail'),
    path("profiles/<int:pk>/", views.UserProfileDetailAPIView.as_view(), name='profile_detail'),
]
