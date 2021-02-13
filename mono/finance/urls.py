from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path("", views.index, name='index'),
    path("transaction/<int:transaction_id>", views.transaction_detail, name='transaction_detail'),
    path("transaction", views.transaction, name='transaction_create'),
]