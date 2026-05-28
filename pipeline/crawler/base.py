from dataclasses import dataclass
from typing import Optional

@dataclass
class RawItem:
    source_name: str
    source_type: str
    title: str
    content: str
    link: Optional[str] = None
    published: Optional[str] = None
