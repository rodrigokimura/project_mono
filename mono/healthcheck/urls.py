from django.urls import path

from . import views

app_name = 'healthcheck'

urlpatterns = [
    path('', views.healthcheck, name='healthcheck'),
    path('update_app/', views.github_webhook, name='update_app'),
    path('deploy/', views.Deploy.as_view(), name='deploy'),
]
