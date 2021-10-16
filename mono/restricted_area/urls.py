from django.urls import path

from . import views

app_name = 'restricted-area'

urlpatterns = [
    path(
        '', 
        views.IndexView.as_view(), 
        name='index'
    ),
    path(
        'force-error-500/', 
        views.ForceError500View.as_view(), 
        name='force-error-500'
    ),
    path(
        'view-error-500/', 
        views.ViewError500View.as_view(), 
        name='view-error-500'
    ),
]
