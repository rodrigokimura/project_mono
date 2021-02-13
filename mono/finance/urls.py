from django.conf.urls import url, path
from . import views

app_name = 'finance'

urlpatterns = [
    path("transaction/<int:transaction_id>", views.transaction_detail, name='transaction_detail'),
]