import time

from twisted.trial.unittest import TestCase

from babblelicious.storage import InMemoryStore


class TestStorage(TestCase):

    def test_inmemory_store(self):
        tsq = InMemoryStore(5)
        start = time.time() - 5
        for i in range(10):
            tsq.append({
                'user': 'user %i' % (i,),
                'message': 'message %s' % (i),
                'time': start + i,
            }, timestamp=start + i)

        self.assertEqual([], tsq.since(start + 9))
        [found] = tsq.since(start + 8)
        timestamp, data = found
        self.assertEqual(timestamp, start + 9)
        self.assertEqual(data, {
            'user': 'user 9',
            'message': 'message 9',
            'time': start + 9,
        })
        self.assertEqual(len(tsq), 5)
