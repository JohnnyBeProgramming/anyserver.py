#!/usr/bin/env python3
from anyserver import AnyServer

from example.routes.status import router as STATUS_ROUTES
from example.routes.todo.index import router as TODO_ROUTES
from example.test import router as TEST_ROUTES

app = AnyServer(prefers='FastAPI')


def main():
    app.static("./public")
    app.register(STATUS_ROUTES)
    app.register(TEST_ROUTES)
    #app.register(TODO_ROUTES)
    app.start()


if __name__ == '__main__':
    main()
