import json
import pkg_resources
import time

from twisted.internet.task import Clock
from twisted.trial.unittest import TestCase
from twisted.web.server import NOT_DONE_YET, Site
from twisted.web.test.test_web import DummyRequest

from babblelicious.server import (
    Server, EventSourceResource, TimestampQueue,
    INITIAL_BUFFER, MAX_WAIT)


class TestEventSourceResource(TestCase):

    def setUp(self):
        self.subscribers = set()

    def mk_resource(self, subscribers=None):
        resource = EventSourceResource(subscribers or self.subscribers)
        resource.clock = Clock()
        return resource

    def mk_request(self, method='GET', url=''):
        request = DummyRequest(url.split('/'))
        request.method = method
        return request

    def test_get(self):
        request = self.mk_request()
        resource = self.mk_resource()
        self.assertEqual(resource.render(request), NOT_DONE_YET)

    def test_headers(self):
        request = self.mk_request()
        resource = self.mk_resource()
        self.assertEqual(resource.render(request), NOT_DONE_YET)
        headers = request.outgoingHeaders
        self.assertEqual(headers['content-type'], 'text/event-stream')
        self.assertEqual(headers['cache-control'], 'no-cache')
        self.assertEqual(headers['access-control-allow-origin'], '*')

    def test_write_two_bytes_blank(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertEqual(request.written, [INITIAL_BUFFER, '\n\n'])

    def test_subscribe(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertTrue(request in self.subscribers)

    def test_unsubscribe(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertTrue(request in self.subscribers)
        request.finish()
        self.assertFalse(request in self.subscribers)

    def test_broadcast(self):
        get_request = self.mk_request()
        resource = self.mk_resource()
        resource.render(get_request)

        post_request = self.mk_request()
        post_request.method = 'POST'
        post_request.args['user'] = ['foo']
        post_request.args['message'] = ['bar']
        resource.render(post_request)

        broadcast_msg = get_request.written[-1]
        self.assertEqual(
            broadcast_msg,
            'id: 0.0\n' +
            'data: %s' % json.dumps({
                'message': 'bar',
                'user': 'foo',
            }) +
            '\n\n')

    def test_close(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertFalse(request.finished)
        resource.clock.advance(MAX_WAIT)
        self.assertTrue(request.finished)

    def test_closing_already_closed(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertEqual(None, resource.close(request))

    def test_server(self):
        site = Site(Server())
        redirect = site.getResourceFor(self.mk_request('GET', ''))
        self.assertEqual(redirect.url, 'static/index.html')
        static = site.getResourceFor(self.mk_request('GET', 'static'))
        self.assertEqual(
            static.path,
            pkg_resources.resource_filename('babblelicious', 'static'))

    def test_timestamp_queue(self):
        tsq = TimestampQueue(5)
        start = time.time() - 5
        for i in range(10):
            tsq.append(
                'user %i' % (i,),
                'message %s' % (i),
                timestamp=start + i)

        self.assertEqual([], tsq.since(start + 9))
        [found] = tsq.since(start + 8)
        timestamp, data = found
        self.assertEqual(timestamp, start + 9)
        self.assertEqual(data, {
            'user': 'user 9',
            'message': 'message 9',
        })
