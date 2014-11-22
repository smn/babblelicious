import sys
import yaml

from twisted.python import usage, log
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.web.server import Site

from babblelicious.server import Server


class Options(usage.Options):

    optParameters = [
        ['endpoint', 'e', 'tcp:8081', 'The endpoint to listen on.'],
        ['config', 'c', 'babblelicious.yaml', 'The config to read.'],
    ]


def main():

    options = Options()
    try:
        options.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)

    log.startLogging(sys.stdout)

    with open(options['config']) as fp:
        server_config = yaml.safe_load(fp)

    endpoint = serverFromString(reactor, options['endpoint'])
    endpoint.listen(Site(Server(server_config)))

    reactor.run()
