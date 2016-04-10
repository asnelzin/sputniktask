from django.conf.urls import url

from sputniktask.apps.marvel.views import (ComicsListWithTitle,
                                           HeroEventsList,
                                           ComicsListWithSimilarAuthors,
                                           ComicsListWithSimilarCharacters,
                                           ComicsListFromSameSeries)

urlpatterns = [
    url(r'^comics/', ComicsListWithTitle.as_view(), name='comics-list'),

    url(r'^events/(?P<hero_id>[0-9]+)/', HeroEventsList.as_view(), name='hero-events'),

    url(r'similar/(?P<comic_id>[0-9]+)/byauthors/',
        ComicsListWithSimilarAuthors.as_view(), name='similar-by-authors'),
    url(r'similar/(?P<comic_id>[0-9]+)/bycharacters/',
        ComicsListWithSimilarCharacters.as_view(), name='similar-by-characters'),
    url(r'similar/(?P<comic_id>[0-9]+)/byseries/',
        ComicsListFromSameSeries.as_view(), name='similar-by-series'),
]
