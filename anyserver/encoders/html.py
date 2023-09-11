
from anyserver.encoder import Encoder


class HtmlEncoder(Encoder):
    mime = "text/html"
    ext = [".htm", ".html", ".htmx"]
    def encode(self, data): return '<head></head><body>{}</body>'.format(data)
    def decode(self, data): return '{}'.format(data)

