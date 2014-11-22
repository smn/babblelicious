from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

import treq


class FBAccessTokenResource(Resource):

    def __init__(self, uri, app_id, app_secret):
        self.uri = uri
        self.app_id = app_id
        self.app_secret = app_secret

    def render_GET(self, request):
        redirect_uri = '%s/%s' % (
            self.uri, '/'.join(filter(None, request.prepath)))
        [code] = request.args['code']
        d = treq.get((
            'https://graph.facebook.com/oauth/access_token'
            '?client_id={app_id}'
            '&redirect_uri={redirect_uri}'
            '&client_secret={app_secret}'
            '&code={code}').format(
                app_id=self.app_id,
                app_secret=self.app_secret,
                redirect_uri=redirect_uri,
                code=code))

        def done(response):
            return treq.content(response)

        def got_body(body, request):
            print 'body!!', body
            request.redirect('/')
            request.finish()
            return ''

        d.addCallback(done)
        d.addCallback(got_body, request)
        return NOT_DONE_YET


class AuthenticationResource(Resource):

    def __init__(self, uri, app_id, app_secret):
        Resource.__init__(self)
        self.uri = uri
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_resource = FBAccessTokenResource(uri, app_id, app_secret)

    def getChild(self, name, request):
        if name:
            return {
                'access': self.access_resource,
            }[name]
        return self

    def render_GET(self, request):
        redirect_url = '%s/%s/access' % (
            self.uri, '/'.join(filter(None, request.prepath)))
        request.redirect(
            'https://www.facebook.com/dialog/oauth'
            '?client_id={0}'
            '&redirect_uri={1}'
            '&scope=public_profile,user_friends,email'.format(
                self.app_id, redirect_url))
        return ''


class FacebookAuth(object):

    def __init__(self, url, app_id, app_secret):
        self.url = url
        self.app_id = app_id
        self.app_secret = app_secret

    def resource(self):
        return AuthenticationResource(self.url, self.app_id, self.app_secret)
