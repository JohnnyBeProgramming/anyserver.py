#!/usr/bin/env python3
from anyserver.server import AnyServer

app = AnyServer()


def main():
    app.discover()
    app.start()


if __name__ == '__main__':
    main()
