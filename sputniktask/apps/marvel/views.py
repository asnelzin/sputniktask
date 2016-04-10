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

    Response object is the same as in developer.marvel.com
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
              required: true
              type: string
              paramType: query
            - name: limit
              required: false
              type: int
              paramType: query
            - name: offset
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
              required: false
              type: int
              paramType: query
            - name: offset
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
