"""Shiper's urls"""
from django.urls import path

from . import views

app_name = 'shipper'

urlpatterns = [
    path('', views.ShipView.as_view(), name='root'),
    path('ships/', views.ShipCreateView.as_view(), name='ship_create'),
    path('ships/<uuid:pk>/', views.ShipDetailView.as_view(), name='ship_detail'),
]
