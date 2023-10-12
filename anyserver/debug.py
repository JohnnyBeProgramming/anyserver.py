
import logging
import os
import sys


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


class DEBUG:

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
        printIf = DEBUG.printIf
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
    def default_encoding(ctype, accept=''):
        # Trim extra long headers
        max = 48
        accepts = accept[:max] + '...' if len(accept) > max else accept
        accepts = accepts or '*'
        if ctype and ctype in accepts:
            ctype_b = C.RESET + C.success(ctype) + C.RESET + C.DIM
            accepts = C.dim(accepts.replace(ctype, ctype_b))

        print(C.dim(" « encodes: "), C.bright(ctype),
              C.dim(" # <-- Accepts: "), C.dim(accepts))

    @staticmethod
    def template_found(path, ctype, found, accept=''):

        # List all the accepted ctypes
        max = 48
        accepts = accept[:max] + '...' if len(accept) > max else accept
        accepts = accepts or '*'
        if ctype and ctype in accepts:
            ctype_b = C.RESET + C.bright(ctype) + C.RESET + C.DIM
            accepts = C.dim(accepts.replace(ctype, ctype_b))

        print(C.dim(" « renders: "), C.bright(C.BOLD + found),
              C.dim(" # <-- Accepts: "), C.dim(accepts))

    @staticmethod
    def req_start(req):
        print(C.dim(" « request: "), C.bright(C.BOLD + 'STARTED'))
    def req_end(req):
        print(C.dim(" « request: "), C.success(C.BOLD + 'FINISH'))
        print(C.dim(" « request: "), C.error(C.BOLD + 'FAILED'))
