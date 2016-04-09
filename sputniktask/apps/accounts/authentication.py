from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import ExpiringToken


class ExpiringTokenAuthentication(TokenAuthentication):

    model = ExpiringToken

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        if not token.user.is_superuser and token.expired():
            raise exceptions.AuthenticationFailed('Token has expired')

        return token.user, token
