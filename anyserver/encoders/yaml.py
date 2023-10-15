
import io

from anyserver.encoders.core import Encoder


class YamlEncoder(Encoder):
    mime = "application/yaml"
    ext = [".yaml"]

    def __init__(self, yaml):
        # Provide the yaml module (we have no assurances its installed / importable)
        self.yaml = yaml

    def encode(self, data):
        with io.StringIO() as buffer:
            self.yaml.dump(data, buffer, default_flow_style=False)
            return buffer.getvalue()

    def decode(self, data):
        with io.StringIO(initial_value=data) as stream:
            return self.yaml.safe_load(stream)
