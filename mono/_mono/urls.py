from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# import debug_toolbar

from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls)),

    path('accounts/', include('accounts.urls')),
    path('ms/', include('messenger.urls')),
    path('pm/', include('project_manager.urls')),
    path('hc/', include('healthcheck.urls')),
    path('fn/', include('finance.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),
]
#     prefix_default_language=False
# )

urlpatterns += [path('i18n/', include('django.conf.urls.i18n'))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
