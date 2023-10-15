
from anyserver.domain.models.base import Serializable


class WebResponse(Serializable):
    def __init__(self, verb, path, head, body, status=200):
        self.verb = verb
        self.path = path
        self.status = status
        self.head = head
        self.body = body
