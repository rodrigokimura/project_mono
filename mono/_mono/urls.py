import logging
from rest_framework.authtoken import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .ascii_arts import ascii_art_1
from finance.urls import router as finance_router
# from project_manager.urls import router as project_manager_router
# from filebrowser.sites import site
# import debug_toolbar


urlpatterns = [
    # path('admin/filebrowser/', site.urls),
    # path('grappelli/', include('grappelli.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('', include('homepage.urls')),
    path('maintenance-mode/', include('maintenance_mode.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
    path('accounts/', include('accounts.urls')),
    path('ms/', include('messenger.urls')),
    path('pm/', include('project_manager.urls')),
    # path('pm/api/', include(project_manager_router.urls)),
    path('hc/', include('healthcheck.urls')),
    path('fb/', include('feedback.urls')),
    path('fn/', include('finance.urls')),
    path('fn/api/', include(finance_router.urls)),
    path('bl/', include('blog.urls')),
    path('todo/', include('todo_lists.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Aesthetics-only
logger = logging.getLogger("mylogger")
logger.info(ascii_art_1)
