from abc import ABC
import re

from urllib.request import urlopen, Request

from anyserver.config import AnyConfig
from anyserver.utils.tracer import TRACER, trace


class WebRouter(ABC):

    def __init__(self, prefix='', routes=None):
        self.prefix = prefix or ''
        self.routes = routes if routes else {}

    def register(self, router):
        # Get the raw list of routes, eg: routes[VERB][path] = func(req, resp)
        routes = router.all_routes() if isinstance(router, WebRouter) else router

        # Update our internal routes
        for verb in routes:
            # Create verb entry if not exist
            for sub_path in routes[verb]:
                # Register the route in this we
                prefix = self.prefix or ''
                route = prefix + sub_path
                action = routes[verb][sub_path]
                if AnyConfig.is_dev:
                    # In development mode, we print request details
                    action = self.tracer(verb, route, action)
                self.route(verb, route)(action)

    def route(self, verb, route):
        def decorator(action):
            http = self.routes
            http[verb] = {} if not verb in http else http[verb]
            http[verb][route] = action
            return action
        return decorator

    def all_routes(self):
        # Get the parse list of routes that are registered
        http = {}
        prefix = self.prefix if self.prefix != '/' else ''
        routes = self.routes
        for verb in routes:
            http[verb] = {} if not verb in http else http[verb]

            # Create verb entry if not exist
            for sub_path in routes[verb]:
                action = routes[verb][sub_path]
                route = prefix + sub_path
                http[verb][route] = action

        return http

    def find_route(self, verb, path):
        # Search locally registered routes for a route handler
        if not self.routes or not verb in self.routes:
            return None
        routes = list(self.routes[verb].keys())
        routes.sort(reverse=True, key=len)
        matched = [r for r in routes if re.search(r, path)]
        if len(matched) > 0:
            route = matched[0]  # Return the first match
            return self.routes[verb][route]
        else:
            return None

    def default(self, verb, path):
        # This method should be extended by a server implementation
        message = "You need to implement the `default(self, verb, path)` function.\n"
        message += "Verb: %s, Path: %s\n" % (verb, path)
        raise Exception('FATAL: %s' % message)

    def head(self, path): return self.route("HEAD", path)

    def get(self, path): return self.route("GET", path)

    def post(self, path): return self.route("POST", path)

    def put(self, path): return self.route("PUT", path)

    def patch(self, path): return self.route("PATCH", path)

    def delete(self, path): return self.route("DELETE", path)

    def tracer(self, verb, path, action):
        # Define a simple function that can help us trace through requests in DEV mode
        def wrapped(*args, **kwargs):
            try:
                TRACER.req_start(verb, path, *args, **kwargs)
                data = action(*args, **kwargs)
            except Exception as ex:
                TRACER.req_fail(verb, path, ex)
                raise ex
            return data
        return wrapped

    def proxy(self, url, req):
        if not url:
            raise Exception("FATAL: No proxy URL has been set up.")

        url = '{}{}'.format(url, req.path)
        trace(' ~ Proxy me: %s' % url)

        # Populate the new request with the headers that was requested from client
        headers = {}
        for key in req.head:
            name = key.lower()
            value = req.head[key]
            if name == "host":  # <-- Trick endpoint into thinking its a direct call
                proxy_host = url.replace('http://', '')
                proxy_host = proxy_host.replace('https://', '')
                proxy_host = proxy_host.replace('localhost', '127.0.0.1')
                proxy_host = proxy_host.split('/')[0]
                value = proxy_host
                pass
            if name.startswith('x-') or name.startswith('sec-') or name in (
                'connection',
                'user-agent'
            ):
                pass  # <-- Filtering out noise and tracers we dont need
            else:
                headers[key] = value

        # Create a new request handler, then fetch the response via a proxied request
        req = Request(url, headers=headers)
        resp = urlopen(req)
        return resp
