import os
import logging
import importlib

from glob import glob

from anyserver.routers.router import WebRouter
from anyserver.utils.tracer import TRACER
from anyserver.encoders.core import Encoder

logger = logging.getLogger('templates')


class TemplateRouter(WebRouter):
    cache = {}

    def __init__(self, prefix='', base="./templates", routes=None, encoders=None):
        super().__init__(prefix, routes)
        self.base = base
        self.views = {}
        self.default_enc = 'application/json'
        self.encoders = {}
        self.jinja2 = None

        # Map all known encoders for later use
        encoders = encoders if encoders else Encoder.all()
        for enc in encoders:
            self.encoders[enc.mime] = enc

    def templates(self, path):
        self.base = path

    def renders(self, path, content_type=''):
        if not self.jinja2:
            try:
                # Try and load the jnja templates (if installed)
                self.jinja2 = importlib.import_module('jinja2')
            except ImportError:
                message = "If you use render templates, you need to install jinja2"
                raise Exception(message)

        def decorator(action):
            # Save a ref for this action, linked to the template path
            self.cache[action] = path

            # Now lets try and load all known templates for this path
            self.add_views(path, content_type)
            return self.render(action)  # Render best matching template

        return decorator

    def content_type(self, req, resp, path=None):
        # Try and resolve the template by path and content type
        accept = req.head['accept'] if 'accept' in req.head else ''
        ctype = resp.head['content-type'] if 'content-type' in resp.head else ''
        ctype = '' if ctype == 'application/x-www-form-urlencoded' else ctype

        # Check for edge case where HTMX content is submitted with a form
        if 'hx-request' in req.head:
            return 'text/html'

        # Content type was specified, use as is (dont try and modify)
        if not ctype:
            # Try and find a content type from the accepted content types
            # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
            views = self.views
            view_types = [] if not path in views else list(views[path].keys())
            for item in [] if not accept else accept.split(','):
                item_type = item.split(';')[0]
                if item_type in view_types:
                    ctype = item_type
                    break
                elif item_type in self.encoders:
                    ctype = item_type
                    break

        return ctype

    def render(self, action):
        # Resolve the template if any were registered
        path = self.cache[action] if action in self.cache else ''

        def wrap_params(req, resp, data):
            return {
                "req": req,
                "resp": resp,
                "request": req,
                "response": resp,
                **data
            }

        ref = action

        def formatted(req, resp, render=None, *args, **kwargs):

            # Get the raw result from the action
            data = action(req, resp, *args, **kwargs)

            # Try and resolve the template by path and content type
            ctype = self.content_type(req, resp, path)
            if ctype:  # Set the response content type (if not already set)
                resp.head['content-type'] = ctype

            # If the result is already a string or bytes, we skip, and assume its already encoded
            if type(data) == str or type(data) == bytes:
                return data

            # Try and resolve a template to apply (given the accepted content types)
            accept = req.head['accept'] if 'accept' in req.head else ''
            filename = self.find_view(path, ctype)
            if filename:
                # Template has been found and will be applied
                TRACER.template_found(filename, accept)
            else:
                # No template, render encoding for content type
                ctype = self.default_enc if not ctype else ctype
                resp.head['content-type'] = ctype
                TRACER.default_encoded(ctype, accept)
                return self.encode(data, ctype)

            # Template found, lets render it (incl. request and response objects)
            params = wrap_params(req, resp, data)
            if render:
                # Custom render action was specified, template was found
                return render(filename, params)
            else:
                # Template found, use default template renderer
                return self.render_template(filename, params)

        return formatted

    def render_template(self, path, data):
        base = self.base
        path = path if not path.startswith("/") else path[1:]
        target = os.path.join(base, path)
        with open(target, 'r') as file:
            content = file.read()
            loader = self.jinja2.FileSystemLoader(base)
            template = self.jinja2.Environment(
                loader=loader).from_string(content)
            return template.render(data)

    def add_views(self, path, ctype=None):
        # Create a collection for the view path(s)
        views = self.views
        views[path] = views[path] if path in views else {}

        # Search for known file types (or only the given content type if specified)
        types = [ctype] if ctype else self.encoders.keys()
        for ctype in types:
            found = self.load_view(path, ctype)
            if found:
                views[path][ctype] = found

    def load_view(self, path, ctype):
        # Check if template for content type is cached
        if ctype and ctype in self.views[path]:
            return self.views[path][ctype]

        # Define the file path prefix (excl. extensions)
        base = self.base
        path = path if not path.startswith("/") else path[1:]
        target = os.path.join(base, path)

        # Try and search the filesystem for mappings to the file types
        found = None
        if ctype in self.encoders and len(self.encoders[ctype].ext):
            # Find the extensions for the given mime type
            files = []
            for ext in set(self.encoders[ctype].ext):
                files.extend(glob(target+"*"+ext))
            if len(files):
                found = files[0]  # Return first matched file template

        # Fallback, if the file target exists (no extended prefixes),
        # load it explicitly as the template.
        if not found and os.path.isfile(target):
            found = target

        # Normalise and make path normal
        found = found[len(base):] if found else None
        found = found[1:] if found and found.startswith("/") else found
        return found

    def find_view(self, path, ctype=None):
        views = self.views
        available = []

        # If no content type specified, we will search for available response types
        if path in views and not ctype and len(list(views[path].keys())):
            # Return the default content type, or the first available type (if no default set)
            default = self.default_enc
            available = list(views[path].keys())
            ctype = default if default in views[path] else available[0]
        else:
            # Fall back to default content type (if not specified)
            ctype = self.default_enc if not ctype else ctype

        # Get the render template by path and content type
        if path in views and ctype in views[path]:
            return views[path][ctype]

        # No render engine found for content type
        return None

    def encode(self, data, ctype=None):
        # Fall back to default content type for encoding
        ctype = self.default_enc if not ctype else ctype

        if ctype not in self.encoders:
            raise Exception('Failed to encode to "%s" content type.' % ctype)

        return self.encoders[ctype].encode(data)
