#!/usr/bin/env python3
from anyserver import AnyServer

from routes.status import router as STATUS_ROUTES
from routes.todo.index import router as TODO_ROUTES
from routes.task import router as TASK_ROUTES

app = AnyServer(pref='FastAPI')
app.static("./public")
app.register(STATUS_ROUTES)
app.register(TODO_ROUTES)


def main():    
    app.start()


if __name__ == '__main__':
    main()
