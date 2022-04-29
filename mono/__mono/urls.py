"""Django URL patterns for the mono app."""
import logging

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

from .ascii_arts import ASCII_ART

# from filebrowser.sites import site
# import debug_toolbar


urlpatterns = [
    # path('admin/filebrowser/', site.urls),
    # path('grappelli/', include('grappelli.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
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
    path('bl/', include('blog.urls')),
    path('cl/', include('checklists.urls')),
    path('nt/', include('notes.urls')),
    path('pixel/', include('pixel.urls')),
    path('watcher/', include('watcher.urls')),
    path('restricted-area/', include('restricted_area.urls')),
    path('shipper/', include('shipper.urls')),
    path('cb/', include('curriculum_builder.urls')),
    path('cd/', include('coder.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
    path('i18n/', include('django.conf.urls.i18n')),
    path('markdownx/', include('markdownx.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Aesthetics-only
logger = logging.getLogger(__name__)
logger.warning('\033[1;32m%s\033[0m', ASCII_ART)
