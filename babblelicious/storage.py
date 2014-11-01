# -*- test-case-name: babblelicious.tests.test_storage -*-
from collections import deque

from twisted.internet import reactor


class InMemoryStore(deque):

    clock = reactor

    def __init__(self, maxlen):
        super(InMemoryStore, self).__init__([], maxlen)

    def append(self, user, message, timestamp=None):
        super(InMemoryStore, self).append((
            timestamp or self.clock.seconds(), {
                'user': user,
                'message': message,
            }))

    def since(self, timestamp):
        return filter(lambda (ts, data): ts > timestamp, self)
