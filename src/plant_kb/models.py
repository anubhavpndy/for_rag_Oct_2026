from dataclasses import dataclass, field
from typing import Any

@dataclass
class ContentUnit:
    text: str
    content_type: str
    source_location: dict[str, Any] = field(default_factory=dict)
    section_name: str | None = None

@dataclass
class ParsedDocument:
    content_units: list[ContentUnit]
    warnings: list[str] = field(default_factory=list)
