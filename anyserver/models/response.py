
from typing import Any, Dict, Optional
from anyserver.models.base import Serializable


class WebResponse(Serializable):
    status: int
    head: Dict[str, str]
    body: Optional[Any]

    def __init__(self, verb, path, status=200, head={}, body=None):
        self.status = status
        self.verb = verb
        self.path = path
        self.head = head
        self.body = body
