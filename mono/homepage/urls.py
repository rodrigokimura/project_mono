from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.HomepageView.as_view(), name='home'),
    # path('', RedirectView.as_view(pattern_name='finance:index'), name='home'),
]
