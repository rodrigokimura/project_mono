from django.urls import path
from . import views

app_name = 'pixel'

urlpatterns = [
    path('pixel.gif', views.pixel_gif, name='pixel_gif'),
]
