from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from backend.domain.enums import EvidenceType


@dataclass
class EvidenceSource:
    id: str
    parent_ulpin: str
    evidence_type: EvidenceType
    provider: str
    source_reference: str
    checksum: str
    crs: Optional[str] = None
    acquisition_time: Optional[datetime] = None
    processing_version: str = "1.0.0"
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.id:
            raise ValueError("Evidence ID cannot be empty.")
        if not self.checksum:
            raise ValueError("Evidence source must contain a valid checksum.")
        if not self.parent_ulpin or len(self.parent_ulpin) != 14:
            raise ValueError("Evidence must be associated with a valid 14-digit parent ULPIN.")
