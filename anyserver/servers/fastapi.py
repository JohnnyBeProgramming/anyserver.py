import logging
import os

from anyserver.router import WebRequest, WebResponse
from anyserver.servers.abstract import AbstractServer, OptionalModule

# Bootstrap the flask module (if available amd installed as a dependency)
uvicorn = OptionalModule('uvicorn', ['run'])
fastapi = OptionalModule('fastapi', [
    'APIRouter',
    'FastAPI',
    'Request',
    'Response'
])
fastapiStatic = OptionalModule('fastapi.staticfiles', ['StaticFiles'])


def tryFastAPIServer(app=None, config=None, prefix=''):
    found = uvicorn.found() and fastapi.found() and fastapiStatic.found()
    if not found or (app and not fastapi.hasBase(app, 'FastAPI')):
        return None  # App instance is not a Flask Application, skip...
    try:
        # Load the flask server if the dependencies are installed
        return FastAPIServer(prefix, config, app)
    except Exception:
        return None


class FastAPIServer(AbstractServer):
    """
    Define a server instance that uses FastAPI ans the underlying engine
    """

    class Request(WebRequest):
        # Wrap your request object into serializable object
        def __init__(self, ctx): super().__init__(
            verb=ctx.method,
            path=ctx.url.path,
            head=ctx.headers,
            body=None,
            params={},
        )

    class Response(WebResponse):
        __sent = False

        # Wrap your response object into serializable object
        def __init__(self, ctx, req):
            super().__init__(
                verb=req.method,
                path=req.url.path,
                head={},
                body=None
            )

        def redirect(self, ctx, location):
            self.status = 302
            self.head['Location'] = location

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
        self.app = app if app else fastapi.FastAPI()
        super().__init__(prefix, config, self.app)

    def start(self):
        self.onStart()

        # Mount the static path afetr all routes were registered
        static = self.config.static
        if static and os.path.isdir(static):
            fileserver = fastapiStatic.StaticFiles(directory=static, html=True)
            self.app.mount("/", fileserver, name="static")

        # Start the server using the target (request handler) type
        debug = self.config.debug
        imports = self.config.reloads
        if debug and not imports:
            logging.warn('WARNING: Live reload mode has been disabled.')
            logging.warn(' - To use live reload, speficy the app entrypoint.')
            logging.warn('   eg: config["reloads"] = "main:app.app"')
            debug = False

        host = self.config.host
        port = self.config.port
        handle = self.app if not imports else imports
        uvicorn.run(handle, host=host, port=port, reload=debug)

    def static(self, path):
        self.config.static = path # Will be loaded on start

    def route(self, verb, route):
        print(' + [ %-5s ] %s' % (verb, route))


        # Register all routes with the current flask server
        def decorator(action):
            Request = fastapi.Request
            Response = fastapi.Response

            async def respond(request: Request, response: Response):
                async def _body():
                    if not request.method in ["POST", "PUT", "PATCH"]:
                        return None

                    # Parse the body according to the content type
                    ctype = request.headers['content-type'] if 'content-type' in request.headers else None
                    match ctype:
                        case 'application/json':
                            return await request.json()
                        case 'application/x-www-form-urlencoded':
                            return await request.form()

                    return await request.body()

                # Service the incomming request with the specified handler
                # def template(path, data): return render_template(path, **data)
                req = FastAPIServer.Request(request)
                req.body = await _body()  # Fetch the body (async)
                resp = FastAPIServer.Response(response, request)

                data = self.render(action)(req, resp)
                ctype = None if not 'content-type' in resp.head else resp.head['content-type']
                if type(data) == str:
                    return fastapi.Response(content=data, media_type=ctype)

                return data

            # Register the route handler with flask's internal route handling
            # eg: @app.<VERB>(<ROUTE>)
            app = self.app
            router = fastapi.APIRouter()
            router.add_api_route(route, respond, methods=[verb])
            app.include_router(router)

            return action

        return decorator
