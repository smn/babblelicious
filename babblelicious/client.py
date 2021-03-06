# -*- test-case-name: babblelicious.tests.test_client -*-
import pkg_resources
from datetime import datetime

from jinja2 import Environment, PackageLoader
from klein import Klein

from twisted.web.static import File


class Client(object):

    app = Klein()

    def __init__(self, storage, root_path=''):
        self.storage = storage
        self.root_path = root_path
        self.env = Environment(
            loader=PackageLoader('babblelicious', 'templates'))
        self.env.filters['format_timestamp'] = self.filter_format_timestamp

    def filter_format_timestamp(self, value, format):
        return datetime.fromtimestamp(value).strftime(format)

    def resource(self):
        return self.app.resource()

    @app.route('/')
    def index(self, request):
        template = self.env.get_template('index.html')
        return template.render(
            storage=self.storage,
            STATIC_URL='{0}/static'.format(self.root_path))

    @app.route('/static/', branch=True)
    def static(self, request):
        return File(pkg_resources.resource_filename('babblelicious', 'static'))
