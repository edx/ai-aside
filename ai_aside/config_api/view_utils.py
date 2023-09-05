"""
Config API Utilities
"""
import logging

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_aside.config_api.exceptions import AiAsideException
from ai_aside.config_api.permissions import HasStudioWriteAccess

log = logging.getLogger(__name__)


def handle_ai_aside_exception(exc, name=None):  # pylint: disable=inconsistent-return-statements
    """
    Converts ai_aside exceptions into restframework responses
    """
    if isinstance(exc, AiAsideException):
        log.exception(name)
        return APIResponse(http_status=exc.http_status, data={'message': str(exc)})


class APIResponse(Response):
    """API Response"""
    def __init__(self, data=None, http_status=None, content_type=None, success=False):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {'response': {'success': success}}
        reply['response'].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


class AiAsideAPIView(APIView):
    """
    Base API View with authentication and permissions.
    """

    authentication_classes = (JwtAuthentication, SessionAuthentication,)
    permission_classes = (HasStudioWriteAccess,)

    def handle_exception(self, exc):
        """
        Converts ai-aside exceptions into standard restframework responses
        """
        resp = handle_ai_aside_exception(exc, name=self.__class__.__name__)
        if not resp:
            resp = super().handle_exception(exc)
        return resp
