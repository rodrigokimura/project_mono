from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('accounts/', include('accounts.urls')),
    path('ms/', include('messenger.urls')),
    path('pm/', include('project_manager.urls')),
    path('hc/', include('healthcheck.urls')),
    path('fn/', include('finance.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]

if settings.DEBUG :
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
