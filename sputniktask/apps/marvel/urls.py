from django.conf.urls import url

from sputniktask.apps.marvel.views import ComicsListWithTitle

urlpatterns = [
    url(r'^comics/', ComicsListWithTitle.as_view(), name='comics-list'),
]
