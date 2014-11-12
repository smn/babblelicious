import sys

from twisted.python import usage, log
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.web.server import Site

from babblelicious.server import Server


class Options(usage.Options):

    optParameters = [
        ['endpoint', 'e', 'tcp:8081', 'The endpoint to listen on.'],
        ['fb-auth-url', 'u', 'http://localhost:8081/',
         'The URL this service is available on (used for auth callbacks).'],
        ['fb-app-id', 'a', None,
         'The Facebook app-id (used for auth callbacks).'],
        ['fb-app-secret', 's', None,
         'The Facebook app-secret (used for auth callbacks).'],
    ]

    def postOptions(self):
        print dict(self)
        if not all([self['fb-app-id'], self['fb-app-secret']]):
            raise usage.UsageError(
                "Please specify FB app-id and app-secret for auth callbacks.")


def main():

    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    log.startLogging(sys.stdout)

    endpoint_str = options['endpoint']
    endpoint = serverFromString(reactor, endpoint_str)
    endpoint.listen(
        Site(
            Server(
                options['fb-app-id'],
                options['fb-app-secret'],
                options['fb-auth-url'])))

    reactor.run()
