from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authtoken.models import Token


class ExpiringToken(Token):

    class Meta(object):
        proxy = True

    def expired(self):
        now = timezone.now()
        token_lifespan = getattr(settings, 'TOKEN_LIFESPAN', timedelta(hours=24))
        return self.created + token_lifespan < now
