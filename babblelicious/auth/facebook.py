# -*- test-case-name: babblelicious.auth.tests.test_facebook -*-

from twisted.internet import reactor
from twisted.web.client import HTTPConnectionPool
from twisted.web.resource import Resource, NoResource
from twisted.web.server import NOT_DONE_YET

import treq


class FBAccessTokenResource(Resource):

    DEFAULT_TIMEOUT = 10
    ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

    def __init__(self, uri, app_id, app_secret, pool=None):
        self.uri = uri
        self.app_id = app_id
        self.app_secret = app_secret
        self.pool = pool

    def request(self, method, url, **kwargs):
        """
        Make an HTTP request.
        Uses ``treq`` internally and applies the ``DEFAULT_TIMEOUT`` as
        per the configuration.

        :returns: twisted.web.iweb.IResponse

        """
        defaults = {
            'pool': self.pool,
            'auth': None,
            'timout': self.DEFAULT_TIMEOUT,
        }
        defaults.update(kwargs)
        return treq.request(method.encode('utf-8'), url.encode('utf-8'),
                            **defaults)

    def render_GET(self, request):
        redirect_uri = '%s/%s' % (
            self.uri, '/'.join(filter(None, request.prepath)))
        [code] = request.args['code']
        d = self.request('GET', (
            '{url}'
            '?client_id={app_id}'
            '&redirect_uri={redirect_uri}'
            '&client_secret={app_secret}'
            '&code={code}').format(
                url=self.ACCESS_TOKEN_URL,
                app_id=self.app_id,
                app_secret=self.app_secret,
                redirect_uri=redirect_uri,
                code=code))

        def done(response):
            return treq.content(response)

        def got_body(body, request):
            request.redirect('/')
            request.finish()
            return ''

        d.addCallback(done)
        d.addCallback(got_body, request)
        return NOT_DONE_YET


class AuthenticationResource(Resource):

    def __init__(self, uri, app_id, app_secret, pool=None):
        Resource.__init__(self)
        self.uri = uri
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_resource = FBAccessTokenResource(
            uri, app_id, app_secret, pool=pool)

    def getChild(self, name, request):
        return {
            'access': self.access_resource,
        }.get(name, NoResource())

    def render_GET(self, request):
        redirect_url = '%s/%s/access' % (
            self.uri, '/'.join(request.prepath))
        request.redirect(
            'https://www.facebook.com/dialog/oauth'
            '?client_id={0}'
            '&redirect_uri={1}'
            '&scope=public_profile,user_friends,email'.format(
                self.app_id, redirect_url))
        return ''


class FacebookAuth(object):

    def __init__(self, url, app_id, app_secret, pool=None):
        self.url = url
        self.app_id = app_id
        self.app_secret = app_secret
        self.pool = pool

    def resource(self):
        return AuthenticationResource(
            self.url, self.app_id, self.app_secret, pool=self.pool)
