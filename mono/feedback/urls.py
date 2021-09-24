from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path("", views.FeedbackCreateView.as_view(), name='feedback_create'),
]
