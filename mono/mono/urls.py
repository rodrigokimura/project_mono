from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('accounts/', include('accounts.urls')),
    path('messenger/', include('messenger.urls')),
    path('hc/', include('healthcheck.urls')),
]
