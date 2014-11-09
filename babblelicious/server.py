# -*- test-case-name-: babblicious.tests.test_server -*-

import json

from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor
from twisted.web.util import Redirect

from babblelicious.client import Client
from babblelicious.storage import InMemoryStore


MAX_WAIT = 25
BACKLOG_SIZE = 25
INITIAL_BUFFER = ' ' * 2048


class EventSourceResource(Resource):

    clock = reactor

    def __init__(self, storage, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.storage = storage
        self.subscribers = set()

    def subscribe(self, request):
        self.subscribers.add(request)

    def unsubscribe(self, request):
        if request in self.subscribers:
            self.subscribers.remove(request)

    def broadcast(self, user, message):
        now = self.clock.seconds()
        data = {
            'user': user,
            'message': message,
            'time': now,
        }
        self.storage.append(data, timestamp=now)
        for subscriber in self.subscribers:
            self.write(subscriber, data)

    def write(self, request, data):
        now = self.clock.seconds()
        data_obj = [
            ("id", now),
            ("data", json.dumps(data)),
        ]
        data_str = '\n'.join(['%s: %s' % kv for kv in data_obj])
        request.write('%s\n\n' % (data_str,))

    def close(self, request):
        try:
            request.finish()
        except RuntimeError:  # pragma: no cover
            pass

    def render_GET(self, request):
        self.subscribe(request)
        request.notifyFinish().addBoth(lambda _: self.unsubscribe(request))
        request.setHeader("Content-Type", "text/event-stream")
        request.setHeader("Cache-Control", "no-cache")
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.write(INITIAL_BUFFER)  # Get some initial data flowing
        request.write('\n\n')
        self.clock.callLater(MAX_WAIT, self.close, request)
        return NOT_DONE_YET

    def render_POST(self, request):
        user = request.args['user'][0]
        message = request.args['message'][0]
        self.broadcast(user, message)
        return ''


class FBAccessTokenResource(Resource):

    def __init__(self, app_id, app_secret)


class AuthenticationResource(Resource):

    def __init__(self, app_id, app_secret, url, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.app_id = app_id
        self.url = url

    def getChild(self, name, request):
        if name:
            return {
                'access': FBAccessTokenResource(self.app_id),
            }[name]
        return self.render_GET(request)

    def render_GET(self, request):
        request.redirect(
            'https://www.facebook.com/dialog/oauth'
            '?client_id={0}'
            '&redirect_uri={1}'.format(self.app_id, self.url))
        return ''


class Server(Resource):
    def __init__(self, app_id, url, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)

        self.putChild('', Redirect('client/'))
        self.putChild('auth', AuthenticationResource(app_id, url))

        storage = InMemoryStore(BACKLOG_SIZE)
        client = Client(storage, root_path='/client')

        self.putChild(
            'event_source', EventSourceResource(storage))
        self.putChild('client', client.resource())
