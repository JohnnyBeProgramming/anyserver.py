import os

from anyserver.utils.tracer import TRACER
from anyserver.utils.optionals import OptionalModule
from anyserver.models.request import WebRequest
from anyserver.models.response import WebResponse
from anyserver.servers.abstract import AbstractServer
from anyserver.utils.entrypoint import Entrypoint

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
        def __init__(self, ctx):
            super().__init__(
                url=str(ctx.url),
                verb=ctx.method,
                path=ctx.url.path,
                head=self._head(ctx.headers),
                body=None,
            )

        def _head(self, headers):
            # Parse the headers (into serializable)
            head = {}
            for key in headers:
                head[key.lower()] = headers[key]
            return head

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
        # Create a router to register incomming events with
        self.app = app if app else fastapi.FastAPI()
        super().__init__(prefix, config, self.app)

        # Auto detect the entrypoint if in development mode
        # This needs to be called in the constructor for it to work
        if self.config.is_dev and not self.config.entrypoint:
            root = Entrypoint.get()
            self.config.entrypoint = f'{root}.app' if root else None

    def start(self):
        self.onStart()

        # Required properties
        host = self.config.host
        port = self.config.port
        static = self.config.static

        # Check if we are running in dev or debug mode
        is_dev = self.config.is_dev
        entrypoint = self.config.entrypoint
        if is_dev and not entrypoint:
            TRACER.warn_no_reload()
            is_dev = False

        # Mount the static path afetr all routes were registered
        if static and os.path.isdir(static):
            fileserver = fastapiStatic.StaticFiles(directory=static, html=True)
            self.app.mount("/", fileserver, name="static")

        # Start the server using the target (request handler) type
        handle = self.app if not entrypoint else entrypoint
        uvicorn.run(handle, host=host, port=port, reload=is_dev)

    def static(self, path):
        self.config.static = path  # Will be loaded on start

    def bind(self, verb, route, action):
        # Register all routes with the current FastAPI server
        Request = fastapi.Request
        Response = fastapi.Response

        async def respond(request: Request, response: Response):
            # Service the incomming request with the specified handler
            req = FastAPIServer.Request(request)
            req.body = await self._body(request)  # Fetch the body (async)
            resp = FastAPIServer.Response(response, request)

            # Call the template handler
            data = self.render(action)(req, resp)

            # Return text if already encoded as string
            if type(data) == str:
                ctype = None if not 'content-type' in resp.head else resp.head['content-type']
                return fastapi.Response(content=data, media_type=ctype)

            return data

        # Register the route handler with flask's internal route handling
        # eg: @app.<VERB>(<ROUTE>)
        router = fastapi.APIRouter()
        router.add_api_route(route, respond, methods=[verb])
        self.app.include_router(router)

    async def _body(self, request: Request):
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
