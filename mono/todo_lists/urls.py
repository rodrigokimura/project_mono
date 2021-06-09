from django.urls import path
from django.views.generic.base import RedirectView
from . import views


app_name = 'todo_lists'


urlpatterns = [

    path('', RedirectView.as_view(pattern_name='project_manager:projects'), name='index'),

    path('list/', views.ListCreateView.as_view(), name='list_create'),
    path('list/<int:pk>/', views.ListDetailView.as_view(), name='list_detail'),
    path('list/<int:pk>/edit/', views.ListUpdateView.as_view(), name='list_update'),
    path('list/<int:pk>/delete/', views.ListDeleteView.as_view(), name='list_delete'),
    path('lists/', views.ListListView.as_view(), name='lists'),

    path('list/<int:list_pk>/item/', views.ItemCreateView.as_view(), name='item_create'),
    path('list/<int:list_pk>/item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('list/<int:list_pk>/item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_update'),
    path('list/<int:list_pk>/item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    path('list/<int:list_pk>/items/', views.ItemListView.as_view(), name='items'),
]
