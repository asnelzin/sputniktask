from django.conf.urls import url

from sputniktask.apps.marvel.views import ComicsListWithTitle, HeroEventsList

urlpatterns = [
    url(r'^comics/', ComicsListWithTitle.as_view(), name='comics-list'),
    url(r'^events/(?P<hero_id>[0-9]+)/', HeroEventsList.as_view(), name='hero-events'),
]
