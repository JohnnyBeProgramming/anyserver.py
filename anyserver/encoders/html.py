
from anyserver.encoders.core import Encoder


class HtmlEncoder(Encoder):
    mime = "text/html"
    ext = [".htm", ".html", ".htmx"]
    def encode(self, data): return '{}'.format(data)
    def decode(self, data): return '{}'.format(data)

