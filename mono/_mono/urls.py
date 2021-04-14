from rest_framework.authtoken import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from finance.views import UserViewSet, TransactionViewSet
# import debug_toolbar


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'transactions', TransactionViewSet)


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', views.obtain_auth_token),
    path('api/', include(router.urls)),

    path('accounts/', include('accounts.urls')),
    path('ms/', include('messenger.urls')),
    path('pm/', include('project_manager.urls')),
    path('hc/', include('healthcheck.urls')),
    path('fb/', include('feedback.urls')),
    path('fn/', include('finance.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
]
#     prefix_default_language=False
# )

urlpatterns += [path('i18n/', include('django.conf.urls.i18n'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
