import signal

from abc import ABC, abstractmethod
from importlib import import_module

from anyserver import GetConfig
from anyserver.utils.tracer import TRACER, traceIf
from anyserver.routers.templates import TemplateRouter


class AbstractServer(TemplateRouter):
    app = None
    config = None

    def __init__(self, prefix='', config=None, app=None):
        config = config if config else GetConfig()
        super().__init__(prefix, base=config.templates, routes=config.routes)
        self.config = config
        self.app = app

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def static(self, path): ...

    @abstractmethod
    def bind(self, verb, route, action): ...

    def route(self, verb, route):
        register = super().route(verb, route)

        # We intercept the route declaration, in order to bind to server implementation
        def decorator(action):
            # Let the server implementation bind the route
            self.bind(verb, route, action)
            # Register the route in the route cache
            register(action)
            return action

        return decorator

    def onStart(self):
        # Show the banner and header info for the current server
        TRACER.server_start(self)
        signal.signal(signal.SIGINT, self.onExit)

    def onExit(self, signum, frame): return exit(1)
