from django.urls import path
from django.conf import settings
from . import views

app_name = 'pixel'

urlpatterns = [
    path('pixel.gif', views.pixel_gif, name='pixel_gif'),
]

if settings.APP_ENV == 'DEV':
    urlpatterns += path('test', views.test, name='test'),
