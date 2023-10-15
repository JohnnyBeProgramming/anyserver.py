#!/usr/bin/env python3
from anyserver import AnyServer

from example.routes.status import router as STATUS_ROUTES
from example.routes.todo.index import router as TODO_ROUTES
from example.test import router as TEST_ROUTES

# Declare the server instance and register all the routes
app = AnyServer(prefers='Default')
app.static("./public")
app.register(STATUS_ROUTES)
app.register(TEST_ROUTES)
#app.register(TODO_ROUTES)

def main():
    app.start()


if __name__ == '__main__':
    main()
