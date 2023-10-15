

from anyserver.encoders.core import Encoder


class TextEncoder(Encoder):
    mime = "text/plain"
    ext = [".txt"]
    def encode(self, data): return '{}'.format(data)
    def decode(self, data): return '{}'.format(data)
