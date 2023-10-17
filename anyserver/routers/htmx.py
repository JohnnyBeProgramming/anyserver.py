from anyserver.models.request import WebRequest
from anyserver.routers.templates import TemplateRouter


class HtmxRequest():

    def __init__(self, req: WebRequest): self.req = req

    @staticmethod
    def isHTMX(req: WebRequest): return req.header('hx-request', False)

    @property
    def prompt(self): return self.req.header('hx-prompt', '')

    @property
    def triggerName(self): return self.req.header('hx-trigger-name', '')

    @property
    def triggerValue(self): return self.req.input(self.triggerName, '')


class HtmxRouter(TemplateRouter):

    def htmx(self, template_path, target=None):
        super().renders(template_path)

        # We intercept the route declaration, in order to bind to server implementation
        def decorator(action):
            return action

        return decorator
