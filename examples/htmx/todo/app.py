import os
from pathlib import Path

from anyserver import TemplateRouter, WebRequest, WebResponse

from .repo import MockedRepository

THIS_DIR = Path(__file__).parent.parent.absolute()

# Create decorator for registering web routes
router = TemplateRouter('/todo', base=f'{THIS_DIR}/templates')
repo = MockedRepository()


@router.get('/')
@router.renders("todo/index")
def todo_index(req: WebRequest, resp: WebResponse):
    return {
        "todos": repo.all(),
        "filter": repo.FILTER
    }


@router.post('/search')
@router.renders("todo/search")
def search_todo(req: WebRequest, resp: WebResponse):
    # Update the current filter (if needed)
    if filter := req.input("filter"):
        repo.FILTER = filter

    # Filter items by search terms
    terms = req.input("search")
    todos = repo.search(terms)
    return {
        "todos": todos,
        "filter": repo.FILTER
    }


@router.post('/')
@router.renders("todo/list-item")
def update_todo(req: WebRequest, resp: WebResponse):
    # Search for the task and make sure it exists
    task_id = req.query.get("id", '')
    found = repo.find(task_id)
    if not found:
        raise Exception(f'Task with id "{task_id}" not found')

    # Process the update action (if any)
    action = req.query.get("action", '')
    match action:
        case "complete":
            # Mark as complete
            found["completed"] = True
            if repo.FILTER == "active":
                # In the case where only active values are filtered, remove the current row
                return ""
        case "restore":
            # Mark as active
            found["completed"] = False
            if repo.FILTER == "completed":
                # In the case where only active values are filtered, remove the current row
                return ""
        case _: pass

    # Return the updated item (rendered as a template to swap out for current displayed item)
    return {"todo": found}


@router.delete('/')
def delete_todo(req: WebRequest, resp: WebResponse):
    # Get the target task ID from the request body
    task_id = req.query.get("id", '')
    delete_all = req.query.get("delete_all", '')

    if delete_all:
        repo.clear()
        # Send back empty placeholder template instead of list
        return router.render_template('todo/empty.html', {})
    elif repo.remove(task_id):
        # Send back empty response (to clear item content on frontend)
        return ""
    else:
        raise Exception(f'Task with id "{task_id}" not found')
