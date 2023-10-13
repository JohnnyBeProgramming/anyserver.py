
import logging
import os
import sys

import yaml

from anyserver.config import Environment


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (
        plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


HAS_COLOR = os.getenv('TERM') and supports_color()


class C:

    RESET = "\u001b[0m" if HAS_COLOR else ""
    BOLD = "\u001b[1m" if HAS_COLOR else ""
    UNDERLINE = "\u001b[4m" if HAS_COLOR else ""
    DIM = "\033[2m" if HAS_COLOR else ""

    BLACK = "\u001b[30m" if HAS_COLOR else ""
    RED = "\u001b[31m" if HAS_COLOR else ""
    GREEN = "\u001b[32m" if HAS_COLOR else ""
    YELLOW = "\u001b[33m" if HAS_COLOR else ""
    BLUE = "\u001b[34m" if HAS_COLOR else ""
    MAGENTA = "\u001b[35m" if HAS_COLOR else ""
    CYAN = "\u001b[36m" if HAS_COLOR else ""
    WHITE = "\u001b[37m" if HAS_COLOR else ""

    @staticmethod
    def dim(msg):
        return f'{C.RESET}{C.DIM}{msg}{C.RESET}'

    @staticmethod
    def bright(msg):
        return f'{C.RESET}{C.WHITE}{msg}{C.RESET}'

    @staticmethod
    def success(msg):
        return f'{C.GREEN}{msg}'

    @staticmethod
    def warning(msg):
        return f'{C.YELLOW}{msg}'

    @staticmethod
    def error(msg):
        return f'{C.RED}{msg}'

    @staticmethod
    def hyperlink(msg):
        return C.RESET + C.UNDERLINE + C.BLUE + msg + C.RESET


class TRACER:

    @staticmethod
    def server_start(server):
        # Display a banner when the server starts up
        TRACER.show_banner(server.__class__.__name__)

        # List all the registered routes
        if routes := server._registered:
            for route, verbs in routes.items():
                for verb in verbs:
                    TRACER.add_route(verb, route)

        # Print server header with config details
        TRACER.print_config(server.config)

    @staticmethod
    def show_banner(server_type='DEFAULT'):
        title = C.bright(C.UNDERLINE + C.BOLD+server_type)
        print(C.DIM + '=' * 64 + C.RESET)
        print(C.WHITE + f'Starting {title}...')
        print(C.DIM + '=' * 64 + C.RESET)

    @staticmethod
    def add_route(verb, route):
        verb = C.bright(C.BOLD + verb.ljust(6, ' ')) + C.DIM
        route = C.bright(route) + C.DIM
        print(C.DIM + f' + [ {verb} ] {route}' + C.RESET)

    @staticmethod
    def printIf(message, value=None):
        if value:
            output = message % C.bright(value)
            print(C.DIM + output + C.RESET)

    @staticmethod
    def print_config(config):
        printIf = TRACER.printIf
        print(C.DIM + '-' * 64 + C.RESET)

        printIf(' + Work Dir: %s', config.working)
        printIf(' + Web Root: %s', config.static)
        printIf(' ~ Proxy To: %s', config.proxy)

        hostname = 'http://%s:%s' % (config.host, config.port)
        hostname = C.hyperlink(hostname)
        print(C.DIM + ' - Hostname: ' + hostname)
        print(C.DIM + '-' * 64 + C.RESET)

    @staticmethod
    def warn_no_reload():
        title = 'WARNING: Live reload mode has been disabled.'
        message = """
- To use live reload, speficy the app entrypoint.
  eg: config["reloads"] = "main:app.app"
"""
        logging.warn(C.warning(title) + C.RESET)
        logging.warn(C.dim(message))

    @staticmethod
    def default_encoded(ctype, accept=''):
        # This method is called when the result was encoded for response
        TRACER.req_end(**{
            "encode": ctype,
        })

    @staticmethod
    def template_found(filename, accept=''):
        # This method is called when the result was rendered in a template
        TRACER.req_end(**{
            "render": filename,
        })

    @staticmethod
    def req_start(verb, path, *args, **kwargs):
        if not Environment.IS_DEV:
            return
        # Try and resolve the request object from the incoming args
        req = args[0] if len(args) > 0 else None
        req = req if req or not "req" in kwargs else kwargs["req"]
        if not req:
            return False

        # Print a header for the incomming request
        fVerb = f'{C.RESET}{C.BOLD}{req.verb}{C.RESET}{C.DIM}'
        fPath = f'{C.RESET}{C.BOLD}{req.path}{C.RESET}{C.DIM}'
        fTail = '-'*(64 - 9 - len(req.verb) - len(req.path))
        print(f'{C.DIM}--» [ {fVerb} {fPath} ] {fTail}')

        if 'hx-request' in req.head:
            TRACER.print_htmx_headers(req)
        if req.body:
            TRACER.req_body(req)

    @staticmethod
    def req_end(**kwargs):
        if not Environment.IS_DEV:
            return
        label = 'DONE' if not "status" in kwargs else kwargs["status"]
        prefix = C.dim("«-- [ ")
        status = C.success(C.BOLD + label)
        suffix = C.dim(' ] ')
        sep = '« ' if len(kwargs.keys()) else ''
        length = 64-9-len(label)
        extra = ''
        for key, val in (kwargs or {}).items():
            if key and key.strip():
                extra += sep + f'{key}: {C.bright(val) + C.RESET + C.DIM}'
                length -= 2 + len(key) + len(val) + len(sep)
                sep = ', '
        fill = C.dim(extra + ' ' + ('-'*length)) + C.RESET
        print(f'{prefix}{status}{suffix}{fill}')

    @staticmethod
    def req_fail(verb, path, error):
        label = 'FAILED'
        message = str(error) if error else ""
        message = message.split("\n")[0]
        prefix = C.dim("«-- [ ")
        status = C.error(C.BOLD + label)
        hint = C.RESET + C.error(C.BOLD + message) + C.RESET + C.DIM
        length = 64-9-len(label) - len(message)
        suffix = C.dim(f' ] {hint} '+'-' * length) + C.RESET
        print(f'{prefix}{status}{suffix}')

    @staticmethod
    def req_head(req, head=None):
        if not head:
            head = {}
            for k in filter(lambda k: k, req.head):
                head[k] = req.head[k]
        print(yaml.safe_dump({"head": head}).rstrip())

    @staticmethod
    def req_body(req):
        if req.body and not type(req.body) in [str, bytes]:
            body = {}
            for k in req.body.keys():
                body[k] = req.body[k]
            print(yaml.safe_dump({"body": body}).rstrip())

    @staticmethod
    def print_htmx_headers(req):
        head = {}
        for key in req.head.keys():
            key = key.lower()
            if key.startswith("hx-") and key != 'hx-request':
                head[key] = req.head[key]
        if head:
            TRACER.req_head(req, head)
