import signal

from importlib import import_module

from anyserver import GetConfig
from anyserver.config import PrintConfig
from anyserver.router import WebRouter
from anyserver.templates import TemplateRouter


class AbstractServer(TemplateRouter):
    app = None
    config = None

    def __init__(self, prefix='', config=None, app=None):
        config = config if config else GetConfig()
        super().__init__(prefix, base=config.templates, routes=config.routes)
        self.config = config
        self.app = app

    def start(self):
        raise Exception('Not implemented: BaseServer.start()')

    def register(self, router):
        # Get the raw list of routes, eg: routes[VERB][path] = func(req, resp)
        routes = router._routes() if isinstance(router, WebRouter) else router

        # Update our internal routes
        for verb in routes:
            # Create verb entry if not exist
            for sub_path in routes[verb]:
                # Register the route in this we
                route = self.prefix + sub_path
                action = routes[verb][sub_path]
                self.route(verb, route)(action)

    def route(self, verb, route):
        raise Exception('Not implemented: BaseServer.route(verb, route)')

    def static(self, path):
        raise Exception('Not implemented: BaseServer.static(path)')

    def onStart(self):
        signal.signal(signal.SIGINT, self.onExit)

        # Print server header with config details
        PrintConfig(self.config)

    def onExit(self, signum, frame): return exit(1)

    def discover(self, path="./routes"):
        print(' - Auto discovering routes in: %s' % path)


class OptionalModule:
    _mod = None
    _name = None

    def __init__(self, name, imports=[]):
        try:
            # Try and load the module and the imports
            self._name = name
            self._mod = self.module()
            for ident in imports:
                setattr(self, ident, self.imports(ident))
        except Exception:
            pass  # Failed to load the module and/or some props

    def imports(self, class_name): return getattr(self.module(), class_name)

    def found(self): return not self._mod == None

    def module(self):
        try:
            name = self._name
            self._mod = self._mod if self._mod else import_module(name)
            return self._mod
        except ImportError:
            raise Exception(f"""
# You are trying to use the '{name}' python package dependency. 
# This dependency was not found, and is not currently installed.
# To install `{name}`, run the following command:

> pip3 install -r requirements.txt {name}

WARNING: Flask python package not found. Aborting!
""")

    def hasBase(self, obj, class_name):
        def all_base_classes(type):
            res = [type.__name__]
            for cls in (cls for cls in type.__bases__ if not cls.__name__ == "object"):
                res = res + all_base_classes(cls)
            return res

        return class_name in all_base_classes(obj.__class__)
