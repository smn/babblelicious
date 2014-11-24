from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.web.client import HTTPConnectionPool

from klein.test_resource import requestMock

from babblelicious.auth.facebook import FacebookAuth
from babblelicious.tests.utils import MockHttpServer


class TestFacebookAuth(TestCase):

    def setUp(self):
        self.pool = HTTPConnectionPool(reactor, persistent=False)
        self.addCleanup(self.pool.closeCachedConnections)

        self.auth = FacebookAuth(
            'http://url', 'app-id', 'app-secret', pool=self.pool)

        self.auth_resource = self.auth.resource()
        self.mock_server = MockHttpServer()
        self.addCleanup(self.mock_server.stop)
        return self.mock_server.start()

    def test_redirect(self):
        request = requestMock('', 'GET')
        request.prepath = ['auth']
        self.auth_resource.render_GET(request)
        self.assertEqual(
            request.headers['Location'],
            ('https://www.facebook.com/dialog/oauth'
             '?client_id=app-id'
             '&redirect_uri=http://url/auth/access'
             '&scope=public_profile,user_friends,email'))

    @inlineCallbacks
    def test_access(self):
        request = requestMock('', 'GET')
        request.prepath = ['auth']
        request.args = {
            'code': ['the-code'],
        }

        access_resource = self.auth_resource.getChild('access', request)
        access_resource.ACCESS_TOKEN_URL = self.mock_server.url
        access_resource.render_GET(request)

        request = yield self.mock_server.get_queue.get()
        self.assertEqual(request.args, {
            'code': ['the-code'],
            'client_id': ['app-id'],
            'client_secret': ['app-secret'],
            'redirect_uri': ['http://url/auth'],
        })
        request.write('')
        request.finish()
