from django.urls import path

from . import views

app_name = 'shipper'

urlpatterns = [
    path('', views.ShipView.as_view(), name='root'),
]
