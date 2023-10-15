
from urllib.parse import parse_qs
from anyserver.domain.models.base import Serializable


class WebRequest(Serializable):

    def __init__(self, url, verb, path, head={}, body=None, query={}):
        self.url = url
        self.verb = verb
        self.path = path
        self.head = head
        self.body = body
        self.query = self._query()

    def _query(self):
        query = {}
        parts = self.url.split('?')[1] if '?' in self.url else ''
        parsed = parse_qs(parts) if parts else {}
        for key in parsed:
            vals = parsed[key]
            vals = vals if len(vals) != 1 else vals[0]
            query[key] = vals
        return query
