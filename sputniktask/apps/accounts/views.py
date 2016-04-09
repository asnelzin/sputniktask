from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .models import ExpiringToken


class ObtainExpiringAuthToken(ObtainAuthToken):

    """
    A view that allows users to exchange their username and password for expiring token.
    """

    model = ExpiringToken

    def post(self, request, *args, **kwargs):
        """
        ---
        type:
            token:
                type: string
                required: true

        consumes:
            - application/json

        produces:
            - application/json

        request_serializer: rest_framework.authtoken.serializers.AuthTokenSerializer
        """
        serializer = AuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            token, _ = ExpiringToken.objects.get_or_create(user=serializer.validated_data['user'])

            if not token.user.is_superuser and token.expired():
                # If the token is expired, generate a new one.
                token.delete()
                token = ExpiringToken.objects.create(user=serializer.validated_data['user'])

            data = {'token': token.key}
            return Response(data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
