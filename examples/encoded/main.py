#!/usr/bin/env python3

from anyserver import AnyServer
from status.index import router

app = AnyServer()
app.register(router)  # Register router with templated responses


def main():
    app.start()


if __name__ == '__main__':
    main()
