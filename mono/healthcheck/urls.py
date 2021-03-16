from django.urls import path
from . import views

urlpatterns = [
    path('', views.healthcheck, name='healthcheck'),
    path('update_app/', views.update_app, name='healthcheck'),
]