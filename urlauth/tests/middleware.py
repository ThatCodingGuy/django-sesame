import logging
from StringIO import StringIO

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import override_settings

from urlauth.backends import ModelBackend


@override_settings(
    AUTHENTICATION_BACKENDS=(
        'django.contrib.auth.backends.ModelBackend',
        'urlauth.backends.ModelBackend',
    ),
    TEMPLATE_CONTEXT_PROCESSORS=(
        'django.contrib.auth.context_processors.auth',
    ),
)
class AuthMiddlewareTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', password='doe')
        self.token = ModelBackend().create_token(self.user)
        self.bad_token = self.token.lower()

        self.log = StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger('urlauth')
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_token(self):
        response = self.client.get('/', {'url_auth_token': self.token})
        self.assertEqual(response.content, 'john')

    def test_bad_token(self):
        response = self.client.get('/', {'url_auth_token': self.bad_token})
        self.assertEqual(response.content, 'anonymous')

    def test_no_token(self):
        response = self.client.get('/')
        self.assertEqual(response.content, 'anonymous')


@override_settings(
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'urlauth.middleware.AuthenticationMiddleware',
    ),
)
class TestAfterAuthMiddleware(AuthMiddlewareTestCase):
    pass


@override_settings(
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'urlauth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ),
)
class TestBeforeAuthMiddleware(AuthMiddlewareTestCase):
    pass


@override_settings(
    MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'urlauth.middleware.AuthenticationMiddleware',
    ),
)
class TestWithoutAuthMiddleware(AuthMiddlewareTestCase):
    pass


@override_settings(
    MIDDLEWARE_CLASSES=(
        'urlauth.middleware.AuthenticationMiddleware',
    ),
)
class TestWithoutSessionMiddleware(AuthMiddlewareTestCase):
    pass
