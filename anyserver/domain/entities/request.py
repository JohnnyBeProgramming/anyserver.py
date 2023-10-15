
from typing import Any, Dict, Optional


class AnyRequest:
    url: str
    verb: str
    path: str
    head: Dict[str, str]
    body: Optional[Any]
    query: Dict[str, str]
