from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('sputniktask.apps.accounts.urls', namespace='accounts')),
    url(r'^api/', include('sputniktask.apps.marvel.urls', namespace='api')),

    url(r'^docs/', include('rest_framework_swagger.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
