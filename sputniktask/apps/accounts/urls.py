from django.conf.urls import url

from .views import ObtainExpiringAuthToken

urlpatterns = [
    url(r'^login/', ObtainExpiringAuthToken.as_view(), name='login')
]
