import pkg_resources

from jinja2 import Environment, PackageLoader
from klein import Klein

from twisted.web.static import File


class Client(object):

    app = Klein()

    def __init__(self, subscribers, root_path=''):
        self.subscribers = subscribers
        self.root_path = root_path
        self.env = Environment(
            loader=PackageLoader('babblelicious', 'templates'))

    def resource(self):
        return self.app.resource()

    @app.route('/')
    def index(self, request):
        template = self.env.get_template('index.html')
        return template.render(
            subscribers=self.subscribers,
            STATIC_URL='{0}/static'.format(self.root_path))

    @app.route('/static/', branch=True)
    def static(self, request):
        return File(pkg_resources.resource_filename('babblelicious', 'static'))
