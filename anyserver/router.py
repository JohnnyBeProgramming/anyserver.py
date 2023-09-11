import re
import json

from urllib.request import urlopen, Request


class Serializable:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class WebRequest(Serializable):
    def __init__(self, verb, path, head={}, body=None, params={}):
        self.verb = verb
        self.path = path
        self.head = head
        self.body = body
        self.params = params


class WebResponse(Serializable):
    def __init__(self, verb, path, head, body, status=200):
        self.verb = verb
        self.path = path
        self.status = status
        self.head = head
        self.body = body


class WebRouter:

    def __init__(self, prefix='', routes=None):
        self.prefix = prefix
        self.routes = routes if routes else {}

    def register(self, router):
        routes = router  # If directly imported

        # Check if routes were registered into a router
        if isinstance(router, WebRouter):
            # Web router was used to register routes
            routes = router._routes()

        # Update our internal routes
        http = self.routes
        for verb in routes:
            # Create verb entry if not exist
            if not verb in http:
                http[verb] = {}
            for sub_path in routes[verb]:
                # Register the route in this we
                route = self.prefix + sub_path
                action = routes[verb][sub_path]
                http[verb][route] = action
                print(' + [ %-5s ] %s' % (verb, route))

    def _routes(self):
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

    def route(self, verb, path):
        routes = self.routes
        if not verb in routes:
            routes[verb] = {}

        def decorator(action):
            routes[verb][path] = action
            return action

        return decorator

    def head(self, path):
        return self.route("HEAD", path)

    def get(self, path):
        return self.route("GET", path)

    def post(self, path):
        return self.route("POST", path)

    def put(self, path):
        return self.route("PUT", path)

    def patch(self, path):
        return self.route("PATCH", path)

    def delete(self, path):
        return self.route("DELETE", path)

    def proxy(self, url, req):
        if not url:
            raise Exception("FATAL: No proxy URL has been set up.")

        url = '{}{}'.format(url, req.path)
        print(' ~ Proxy me: %s' % url)

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
