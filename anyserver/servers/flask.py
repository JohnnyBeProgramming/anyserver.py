import os
import logging

from anyserver.router import WebRequest, WebResponse
from anyserver.servers.abstract import AbstractServer, OptionalModule

# Bootstrap the flask module (if available amd installed as a dependency)
flask = OptionalModule('flask', [
    'Flask',
    'Response',
    'request',
    'redirect',
    'render_template'
])


def tryFlaskServer(app=None, config=None, prefix=''):
    if not flask.found() or (app and not flask.hasBase(app, 'Flask')):
        return None  # App instance is not a Flask Application, skip...
    try:
        # Load the flask server if the dependencies are installed
        return FlaskServer(prefix, config, app)
    except Exception:
        return None


class FlaskServer(AbstractServer):
    """
    Define a server instance that uses Flask ans the underlying engine
    """

    class Request(WebRequest):

        # Wrap your request object into serializable object
        def __init__(self, ctx):
            self.ctx = ctx
            self.head = ctx.headers
            self.params = ctx.args
            self.body = self._body(ctx)
            super().__init__(
                verb=ctx.method,
                path=ctx.path,
                head=self.head,
                params=self.params,
                body=self.body
            )

        def _body(self, ctx):
            if not ctx.method in ["POST", "PUT", "PATCH"]:
                return None

            # Parse the body according to the content type
            ctype = ctx.headers['content-type'] if 'content-type' in ctx.headers else None
            match ctype:
                case 'application/json':
                    return ctx.json
                case 'application/x-www-form-urlencoded':
                    return ctx.form

            return ctx.data

    class Response(WebResponse):
        __sent = False

        # Wrap your response object into serializable object
        def __init__(self, ctx, req):
            self.ctx = ctx

            # Bind properties
            super().__init__(
                verb=req.verb,
                path=req.path,
                head={},
                body=None
            )

        def redirect(self, ctx, location):
            flask.redirect(location, 302)

        def respond(self, ctx, status=200, headers={}, message=""):
            self._resp.status = message
            self._resp.status_code = status
            for key in headers:  # Append headers
                self.head[key] = headers[key]

        def reply(self, ctx, body=None, head={}):
            for key in head:  # Append headers
                self.head[key] = head[key]

            # Send status code (if not sent)
            if not self.__sent:
                self.respond(ctx, self.status)

            # Reply with headers (if not already sent)
            for key in self.head:
                self._resp.headers[key] = self.head[key]

            # Send the response UTF encoded (if defined)
            if body:
                self._resp.data = body

    def __init__(self, prefix='', config=None, app=None):
        app = app if app else flask.Flask(__name__)
        super().__init__(prefix, config, app)

    def start(self):
        # Start the server using the target (request handler) type
        debug = self.config.loglevel == logging.DEBUG
        self.onStart()
        self.app.run(debug=debug, host=self.config.host, port=self.config.port)

    def route(self, verb, route):
        print(' + [ %-5s ] %s' % (verb, route))

        # Register all routes with the current flask server
        def decorator(action):
            def respond(*args, **kwargs):

                req = FlaskServer.Request(flask.request)
                resp = FlaskServer.Response(flask.Response(status=200), req)

                # Service the incomming request with the specified handler
                def template(path, data):
                    return flask.render_template(path, **data)

                # Prepare the response and format the result
                response = resp.ctx
                response.data = self.render(action)(req, resp, render=template)
                for head in resp.head.keys():
                    response.headers[head] = resp.head[head]
                return response

            # Register the route handler with flask's internal route handling
            # eg: @self.app.route(route, methods=[verb])(respond)
            self.app.add_url_rule(
                route, route, view_func=respond, methods=[verb])

            return action
        return decorator

    def static(self, path):
        self.config.static = path

        # Bind the static content to flask's router
        @self.app.route('/', defaults={'path': 'index.html'})
        @self.app.route('/<path:path>')
        def serve_static(path):
            static = os.path.realpath(self.config.static)
            if not os.path.isfile(static + path) and os.path.exists(static + '/' + path + '/index.html'):
                path = path + 'index.html'
            return flask.send_from_directory(static, path)
