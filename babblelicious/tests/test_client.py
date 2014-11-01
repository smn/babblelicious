import time
from datetime import datetime

from twisted.trial.unittest import TestCase

from klein.test_resource import requestMock

from babblelicious.client import Client
from babblelicious.storage import InMemoryStore


class TestClient(TestCase):

    def mk_client(self, storage=None, root_path=''):
        storage = storage or InMemoryStore(50)
        return Client(storage, root_path=root_path)

    def test_index(self):
        client = self.mk_client()
        now = time.time()
        client.storage.append({
            'user': 'foo',
            'message': 'bar',
            'time': now,
        }, timestamp=now)
        request = requestMock("/", "GET")
        client.resource().render(request)
        doc = request.getWrittenData()
        self.assertTrue('<th>foo</th>' in doc)
        self.assertTrue('<td>bar</td>' in doc)
        timestamp = '<td>{0}</td>'.format(
            datetime.fromtimestamp(now).strftime('%H:%M / %d-%m-%Y'),)
        self.assertTrue(timestamp in doc)
