"""Django URL patterns for the mono app."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from markdownx.views import ImageUploadView, MarkdownifyView
from rest_framework.authtoken import views

urlpatterns = [
    path("tinymce/", include("tinymce.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("auth/", include("social_django.urls", namespace="social")),
    path("", include("homepage.urls")),
    path("maintenance-mode/", include("maintenance_mode.urls")),
    path(
        "api-auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
    path("api-token-auth/", views.obtain_auth_token),
    path("accounts/", include("accounts.urls")),
    path("ms/", include("messenger.urls")),
    path("pm/", include("project_manager.urls")),
    path("hc/", include("healthcheck.urls")),
    path("fb/", include("feedback.urls")),
    path("fn/", include("finance.urls")),
    path("bl/", include("blog.urls")),
    path("cl/", include("checklists.urls")),
    path("nt/", include("notes.urls")),
    path("pixel/", include("pixel.urls")),
    path("watcher/", include("watcher.urls")),
    path("restricted-area/", include("restricted_area.urls")),
    path("shipper/", include("shipper.urls")),
    path("cb/", include("curriculum_builder.urls")),
    path("cd/", include("coder.urls")),
    path("mm/", include("mind_maps.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "markdownx/upload/", ImageUploadView.as_view(), name="markdownx_upload"
    ),
    path(
        "markdownx/markdownify/",
        MarkdownifyView.as_view(),
        name="markdownx_markdownify",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
