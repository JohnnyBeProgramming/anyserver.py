
from anyserver.servers.basic import BasicServer
from anyserver.servers.fastapi import tryFastAPIServer
from anyserver.servers.flask import tryFlaskServer

SERVER_TYPES = {
    "FastAPI": tryFastAPIServer,
    "Flask": tryFlaskServer,
    "Default": BasicServer,
}


def AnyServer(app=None, config=None, prefers=None, prefix=''):
    server = None

    # If there is a preferred type, try instantiate that
    if prefers in SERVER_TYPES:
        server = SERVER_TYPES[prefers](app, config, prefix)

    # Now try all of the other registered server types (in the order they were registered)
    for ident in (t for t in SERVER_TYPES if not t == prefers):
        if not server:
            server = SERVER_TYPES[ident](app, config, prefix)
        else:
            break

    # Fall back to the simple server implementation
    if not server:
        server = BasicServer(prefix, config, app)

    return server
