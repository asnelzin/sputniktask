import time
from hashlib import md5

import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_extensions.cache.decorators import cache_response

from sputniktask.apps.accounts.authentication import ExpiringTokenAuthentication
from sputniktask.apps.marvel.serializers import ComicsListSerializer, OffsetPaginationSerializer

from .utils import RequestKeyConstructor


class MarvelAPIRequestFactory(object):
    URL = 'http://gateway.marvel.com:80/v1/public/'

    def get_signature(self):
        ts = str(time.time())
        return {
            'ts': ts,
            'hash': md5(ts + settings.MARVEL_SECRET_KEY + settings.MARVEL_PUBLIC_KEY).hexdigest(),
            'apikey': settings.MARVEL_PUBLIC_KEY,
        }

    def call_api(self, method, params):
        query_params = dict(params, **self.get_signature())
        return requests.get(self.URL + method, params=query_params)


class ComicsListWithTitle(APIView, MarvelAPIRequestFactory):
    """
    Get the list of comics with specific title.

    Response object and errors is described at
    [developer.marvel.com](http://developer.marvel.com/docs#!/public/getComicsCollection_get_6)
    """

    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    api_method = 'comics'

    default_params = {
        'format': 'comic',
        'formatType': 'comic',
        'orderBy': 'focDate',
        'limit': 10,
        'offset': 0,
    }

    @cache_response(key_func=RequestKeyConstructor())
    def get(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - name: title
              description: Required parameter.
              required: true
              type: string
              paramType: query
            - name: limit
              description: 	Limit the result set to the specified number of resources.
              required: false
              type: int
              paramType: query
            - name: offset
              description: Skip the specified number of resources in the result set.
              required: false
              type: int
              paramType: query
        """
        serializer = ComicsListSerializer(data=request.query_params)

        if serializer.is_valid():
            params = self.default_params.copy()
            params.update(**serializer.data)
            response = self.call_api(self.api_method, params)
            return Response(response.json(), status=response.status_code)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class HeroEventsList(APIView, MarvelAPIRequestFactory):
    """
    Get the list of events which related to the provided character.

    Response object and errors is described at
    [developer.marvel.com](http://developer.marvel.com/docs#!/public/getEventsCollection_get_18)
    """
    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    api_method = 'events'

    default_params = {
        'characters': None,
        'limit': 10,
        'offset': 0
    }

    @cache_response(key_func=RequestKeyConstructor())
    def get(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - name: limit
              description: 	Limit the result set to the specified number of resources.
              required: false
              type: int
              paramType: query
            - name: offset
              description: Skip the specified number of resources in the result set.
              required: false
              type: int
              paramType: query
        """
        serializer = OffsetPaginationSerializer(data=request.query_params)
        if serializer.is_valid():
            params = self.default_params.copy()
            params.update(characters=kwargs['hero_id'], **serializer.data)
            response = self.call_api(self.api_method, params)
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ComicsListWithSimilarAuthors(APIView, MarvelAPIRequestFactory):
    """
    Get the list of comics which have similar creators as a provided one.

    Response object and errors is described at
    [developer.marvel.com](http://developer.marvel.com/docs#!/public/getComicsCollection_get_6)
    """

    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    api_method = 'comics'

    default_params = {
        'creators': '',
        'format': 'comic',
        'formatType': 'comic',
        'orderBy': 'focDate',
        'limit': 10,
        'offset': 0
    }

    @cache_response(key_func=RequestKeyConstructor())
    def get(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - name: limit
              description: 	Limit the result set to the specified number of resources.
              required: false
              type: int
              paramType: query
            - name: offset
              description: Skip the specified number of resources in the result set.
              required: false
              type: int
              paramType: query
        """
        serializer = OffsetPaginationSerializer(data=request.query_params)
        if serializer.is_valid():
            response = self.call_api('comics/{}/creators'.format(kwargs['comic_id']), {'limit': 100})
            if response.status_code == 200:
                authors_list = [str(item['id']) for item in response.json()['data']['results']]
                if authors_list:
                    params = self.default_params.copy()
                    creators = '.'.join(authors_list)
                    params.update(creators=creators, **serializer.data)
                    response = self.call_api(self.api_method, params)
                else:
                    return Response({'detail': 'Seems like there is no such comic in Marvel database.'},
                                    status=HTTP_400_BAD_REQUEST)
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ComicsListWithSimilarCharacters(APIView, MarvelAPIRequestFactory):
    """
    Get the list of comics which have similar characters as a provided one.

    Response object and errors is described at
    [developer.marvel.com](http://developer.marvel.com/docs#!/public/getComicsCollection_get_6)
    """

    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    api_method = 'comics'

    default_params = {
        'characters': '',
        'format': 'comic',
        'formatType': 'comic',
        'orderBy': 'focDate',
        'limit': 10,
        'offset': 0
    }

    @cache_response(key_func=RequestKeyConstructor())
    def get(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - name: limit
              description: 	Limit the result set to the specified number of resources.
              required: false
              type: int
              paramType: query
            - name: offset
              description: Skip the specified number of resources in the result set.
              required: false
              type: int
              paramType: query
        """
        serializer = OffsetPaginationSerializer(data=request.query_params)
        if serializer.is_valid():
            response = self.call_api('comics/{}/characters'.format(kwargs['comic_id']), {'limit': 100})
            if response.status_code == 200:
                hero_list = [str(item['id']) for item in response.json()['data']['results']]
                if hero_list:
                    params = self.default_params.copy()
                    characters = '.'.join(hero_list)
                    params.update(characters=characters, **serializer.data)
                    response = self.call_api(self.api_method, params)
                else:
                    return Response({'detail': 'Seems like there is no such comic in Marvel database.'},
                                    status=HTTP_400_BAD_REQUEST)
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ComicsListFromSameSeries(APIView, MarvelAPIRequestFactory):
    """
    Get the list of comics from the same series as a provided one.

    Response object and errors is described at
    [developer.marvel.com](http://developer.marvel.com/docs#!/public/getComicsCollection_get_6)
    """

    authentication_classes = (ExpiringTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    api_method = 'comics'

    default_params = {
        'series': '',
        'format': 'comic',
        'formatType': 'comic',
        'orderBy': 'focDate',
        'limit': 10,
        'offset': 0
    }

    @cache_response(key_func=RequestKeyConstructor())
    def get(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - name: limit
              description: 	Limit the result set to the specified number of resources.
              required: false
              type: int
              paramType: query
            - name: offset
              description: Skip the specified number of resources in the result set.
              required: false
              type: int
              paramType: query
        """
        serializer = OffsetPaginationSerializer(data=request.query_params)
        if serializer.is_valid():
            response = self.call_api('series', {'limit': 1,
                                                'comics': kwargs['comic_id']})
            if response.status_code == 200:
                series_list = [str(item['id']) for item in response.json()['data']['results']]
                if series_list:
                    params = self.default_params.copy()
                    series = series_list[0]
                    params.update(series=series, **serializer.data)
                    response = self.call_api(self.api_method, params)
                else:
                    return Response({'detail': 'Seems like there is no such comic in Marvel database.'},
                                    status=HTTP_400_BAD_REQUEST)
            return Response(response.json(), status=response.status_code)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
