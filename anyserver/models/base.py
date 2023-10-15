
import json


class Serializable:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
