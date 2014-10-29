# -*- test-case-name-: babblicious.tests.test_server -*-

import json
import pkg_resources

from twisted.web.resource import Resource
from twisted.web.static import File
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor
from twisted.web.util import Redirect


subscribers = set([])

MAX_WAIT = 25
INITIAL_BUFFER = ' ' * 2048


class EventSourceResource(Resource):

    clock = reactor

    def __init__(self, subscribers, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.subscribers = subscribers

    def subscribe(self, request):
        self.subscribers.add(request)

    def unsubscribe(self, request):
        if request in self.subscribers:
            self.subscribers.remove(request)

    def broadcast(self, user, message):
        for subscriber in self.subscribers:
            self.write(subscriber, user, message)

    def write(self, request, user, message):
        data_obj = [
            ("id", self.clock.seconds()),
            ("data", json.dumps({
                'user': user,
                'message': message,
            }))
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


class Server(Resource):
    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self.putChild('', Redirect('static/index.html'))
        self.putChild('static', File(
            pkg_resources.resource_filename('babblelicious', 'static')))
        self.putChild('resource', EventSourceResource(subscribers))
