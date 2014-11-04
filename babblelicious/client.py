# -*- test-case-name: babblelicious.tests.test_client -*-
import pkg_resources
from datetime import datetime

from jinja2 import Environment, PackageLoader

from klein import Klein

from twisted.web.static import File
from twisted.internet.defer import succeed


class Client(object):

    app = Klein()

    def __init__(self, storage, root_path=''):
        self.storage = storage
        self.root_path = root_path
        self.env = Environment(
            loader=PackageLoader('babblelicious', 'templates'))
        self.global_context = {
            'STATIC_URL': self.url('/static'),
            'storage': self.storage
        }
        self.env.filters['format_timestamp'] = self.filter_format_timestamp

    def filter_format_timestamp(self, value, format):
        return datetime.fromtimestamp(value).strftime(format)

    def resource(self):
        return self.app.resource()

    def url(self, path):
        return '{0}{1}'.format(self.root_path, path)

    @app.route('/')
    def index(self, request):
        request.redirect(self.url('/room/default/'))
        return succeed(None)

    @app.route('/room/<string:name>/')
    def room(self, request, name):
        template = self.env.get_template(
            'room.html', globals=self.global_context)
        return template.render(name=name)

    @app.route('/static/', branch=True)
    def static(self, request):
        return File(pkg_resources.resource_filename('babblelicious', 'static'))
