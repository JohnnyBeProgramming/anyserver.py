import importlib

from anyserver.encoders.base import Encoder
from anyserver.encoders.csv import CsvEncoder
from anyserver.encoders.html import HtmlEncoder
from anyserver.encoders.json import JsonEncoder
from anyserver.encoders.text import TextEncoder
from anyserver.encoders.yaml import YamlEncoder


# Define common encoders
TEXT = TextEncoder()
HTML = HtmlEncoder()
JSON = JsonEncoder()
CSV = CsvEncoder()

# Register common encoders
Encoder.register(
    HTML,
    TEXT,
    JSON,
    CSV,
)

# -----------------------------------------------------------------
# Load optional encoders only if the dependencies are installed
# -----------------------------------------------------------------
# Try and load the YAML encoder if `yaml` module found
YAML = None
try:
    YAML = YamlEncoder(importlib.import_module('yaml'))
    Encoder.register(YAML)
except ImportError:
    pass  # Module `yaml` not found...
