import json

from twisted.internet.task import Clock
from twisted.trial.unittest import TestCase
from twisted.web.server import NOT_DONE_YET, Site
from twisted.web.test.test_web import DummyRequest

from babblelicious.server import (
    Server, EventSourceResource,
    INITIAL_BUFFER, MAX_WAIT)
from babblelicious.storage import InMemoryStore


class TestEventSourceResource(TestCase):

    def setUp(self):
        self.storage = InMemoryStore(20)

    def mk_resource(self, storage=None):
        storage = storage or self.storage
        resource = EventSourceResource(storage)
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
        self.assertTrue(request in resource.subscribers)

    def test_unsubscribe(self):
        request = self.mk_request()
        resource = self.mk_resource()
        resource.render(request)
        self.assertTrue(request in resource.subscribers)
        request.finish()
        self.assertFalse(request in resource.subscribers)

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
                'time': 0.0,
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
        site = Site(Server({
            'authentication': {
                'backend': 'babblelicious.auth.FacebookAuth',
                'config': {
                    'url': 'http://foo/',
                    'app_id': 'app_id',
                    'app_secret': 'app_secret',
                }
            },
            'storage': {
                'backend': 'babblelicious.storage.InMemoryStore',
                'config': {
                    'maxlen': 50
                }

            }
        }))
        redirect = site.getResourceFor(self.mk_request('GET', ''))
        self.assertEqual(redirect.url, 'client/')

    def test_write_to_backlog(self):
        get_request = self.mk_request()
        resource = self.mk_resource()
        resource.render(get_request)

        post_request = self.mk_request()
        post_request.method = 'POST'
        post_request.args['user'] = ['foo']
        post_request.args['message'] = ['bar']
        resource.render(post_request)
        [entry] = self.storage
        timestamp, data = entry
        self.assertEqual(data, {
            'user': 'foo',
            'message': 'bar',
            'time': 0.0,
        })
