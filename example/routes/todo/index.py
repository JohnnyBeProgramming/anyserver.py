from anyserver import TemplateRouter

from example.routes.todo._data import todos

router = TemplateRouter('/todo', base='./example/templates')


@router.get('/')
@router.renders("todo/home")
def todo_index(req, resp):
    return {"todos": todos}


@router.get('/list')
def todo_list(req, resp):
    return todos


@router.post('/search')
@router.renders("todo/list")
def search_todo(req, resp):
    terms = "" if req.body and not "search" in req.body else req.body["search"]
    found = todos
    if len(terms):
        found = list(filter(lambda todo: terms in todo["title"], todos))
    return {"todos": found}
