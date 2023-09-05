"""
Test utilities.

Since pytest discourages putting __init__.py into testdirectory
(i.e. making tests a package) one cannot import from anywhere
under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes).

So this package is the place to put them.
"""

from unittest.mock import Mock, patch

from rest_framework.test import APITestCase

user_mock = Mock()
user_mock.is_authenticated.return_value = True
user_mock.is_active.return_value = True

JwtAuthenticationMock = Mock()
jwt_authentication_mock = JwtAuthenticationMock.return_value
jwt_authentication_mock.authenticate.return_value = [user_mock, 'fake_token']

SessionAuthenticationMock = Mock()
session_authentication_mock = SessionAuthenticationMock.return_value
session_authentication_mock.authenticate.return_value = [user_mock, None]


class AIAsideAPITestCase(APITestCase):
    """
    Base class for API Tests
    """

    def setUp(self):
        """
        Perform operations common to all tests.
        """
        super().setUp()
        self.jwt_mock = patch('edx_rest_framework_extensions.auth.jwt.authentication.JwtAuthentication',
                              JwtAuthenticationMock)
        self.session_mock = patch('edx_rest_framework_extensions.auth.session.authentication.SessionAuthentication',
                                  SessionAuthenticationMock)
        self.jwt_mock.start()
        self.session_mock.start()

    def tearDown(self):
        """
        Perform common tear down operations to all tests.
        """
        super().tearDown()
        self.jwt_mock.stop()
        self.session_mock.stop()
