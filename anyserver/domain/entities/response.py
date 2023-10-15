
from typing import Any, Dict, Optional


class AnyResponse:
    status: int
    head: Dict[str, str]
    body: Optional[Any]
