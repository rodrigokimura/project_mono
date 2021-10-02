import logging

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from finance.urls import router as finance_router
from rest_framework.authtoken import views

from .ascii_arts import ascii_art_1

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
    path('hc/', include('healthcheck.urls')),
    path('fb/', include('feedback.urls')),
    path('fn/', include('finance.urls')),
    path('fn/api/', include(finance_router.urls)),
    path('bl/', include('blog.urls')),
    path('todo/', include('todo_lists.urls')),
    path('nt/', include('notes.urls')),
    path('pixel/', include('pixel.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
    path('i18n/', include('django.conf.urls.i18n')),
    path('markdownx/', include('markdownx.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Aesthetics-only
logger = logging.getLogger(__name__)
logger.info(ascii_art_1)
