# -*- test-case-name: dishwasher.tests.test_utils -*-
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue, inlineCallbacks

from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource


class MockResource(Resource):
    isLeaf = True

    def __init__(self, get_handler, post_handler, put_handler):
        Resource.__init__(self)
        self.get_handler = get_handler
        self.post_handler = post_handler
        self.put_handler = put_handler

    def render_GET(self, request):
        return self.get_handler(request)

    def render_POST(self, request):
        return self.post_handler(request)

    def render_PUT(self, request):
        return self.put_handler(request)


class MockHttpServer(object):

    def __init__(self, get_handler=None, post_handler=None, put_handler=None):
        self.get_queue = DeferredQueue()
        self.post_queue = DeferredQueue()
        self.put_queue = DeferredQueue()
        self._get_handler = get_handler or self.handle_get_request
        self._post_handler = post_handler or self.handle_post_request
        self._put_handler = put_handler or self.handle_put_request
        self._webserver = None
        self.addr = None
        self.url = None

    def handle_get_request(self, request):
        self.get_queue.put(request)
        return NOT_DONE_YET

    def handle_post_request(self, request):
        self.post_queue.put(request)
        return NOT_DONE_YET

    def handle_put_request(self, request):
        self.put_queue.put(request)
        return NOT_DONE_YET

    @inlineCallbacks
    def start(self):
        root = MockResource(self._get_handler, self._post_handler,
                            self._put_handler)
        site_factory = Site(root)
        self._webserver = yield reactor.listenTCP(
            0, site_factory, interface='127.0.0.1')
        self.addr = self._webserver.getHost()
        self.url = "http://%s:%s/" % (self.addr.host, self.addr.port)

    def stop(self):
        d = self._webserver.stopListening()
        d.addCallback(lambda _: self._webserver.loseConnection())
        return d
