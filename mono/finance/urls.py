from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path("", views.index, name='index'),
    path("transaction/<int:transaction_id>", views.transaction_detail, name='transaction_detail'),
    path("transaction/", views.TransactionCreateView.as_view(), name='transaction_create'),
    path("transaction/<int:pk>/", views.TransactionUpdateView.as_view(), name='transaction_update'),
    path("transaction/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name='transaction_delete'),
    path("transactions/", views.TransactionListView.as_view(), name='transactions'),
]