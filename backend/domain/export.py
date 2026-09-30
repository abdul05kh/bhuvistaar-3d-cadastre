from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class ExportRecord:
    revision_id: UUID
    checksum: str
    exported_by: str
    content: dict
    export_format: str = "JSON"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
