import json

from anyserver.encoder import Encoder


class JsonEncoder(Encoder):
    mime = "application/json"
    ext = [".json"]
    def encode(self, data): return json.dumps(data)
    def decode(self, data): return json.loads(data)

