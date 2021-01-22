from django.conf.urls import url
from . import views

app_name = 'accounts'

urlpatterns = [
    url(r"login/$", views.Login.as_view(),name='login'),
    url(r"logout/$", views.Logout.as_view(), name="logout"),
    url(r"password_change/$", views.PasswordChange.as_view(), name="password_change"),
    url(r"password_change/done/$", views.PasswordChangeDone.as_view(), name="password_change_done"),
    url(r"password_reset/$", views.PasswordReset.as_view(), name="password_reset"),
    url(r"password_reset/done/$", views.PasswordResetDone.as_view(), name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.PasswordResetConfirm.as_view(), name="password_reset_confirm"),
    url(r"reset/done/$", views.PasswordResetComplete.as_view(), name="password_reset_complete"),
    url(r"signup/$", views.sign_up, name="signup"),
]