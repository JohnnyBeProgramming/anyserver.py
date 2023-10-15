#!/usr/bin/env python3
from anyserver import AnyServer

from todo import router as TODO_ROUTES

app = AnyServer()
app.static("./public")
app.register(TODO_ROUTES)


def main():
    app.start()


if __name__ == '__main__':
    main()
