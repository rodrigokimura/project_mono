"""Accounts' urls"""
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name='signup'),
    path("login/", views.Login.as_view(), name='login'),
    path("logout/", views.Logout.as_view(), name='logout'),

    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path("verify/", views.AccountVerificationView.as_view(), name='verify'),
    path("login-as/", views.LoginAsView.as_view(), name='login_as'),
    path("config/", views.ConfigView.as_view(), name='config'),
    path("users/<int:pk>/", views.UserDetailAPIView.as_view(), name='user_detail'),
    path("profiles/<int:pk>/", views.UserProfileDetailAPIView.as_view(), name='profile_detail'),
    path("notifications/<int:pk>/", views.NotificationActionView.as_view(), name='notification_action'),
    path("notifications/count/", views.NotificationCountView.as_view(), name='notification_count'),
    path("notifications/mark-as-read/", views.MarkNotificationsAsReadView.as_view()),
    path("notifications/mark-as-unread/", views.MarkNotificationsAsUnreadView.as_view()),

    path('api/change-password/', views.ChangePasswordView.as_view(), name='api-change-password'),
    path('api-me/', views.ApiMeView.as_view(), name='api_me'),
    path('api-logout/', views.ApiLogoutView.as_view(), name='api_logout'),

    path('plans/', views.PlansView.as_view(), name='plans'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('stripe/webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
]
