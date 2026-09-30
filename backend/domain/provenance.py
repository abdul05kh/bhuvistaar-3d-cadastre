from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional


@dataclass
class ProvenanceRecord:
    revision_id: UUID
    parent_ulpin: str
    generation_method: str = "PRISMATIC_EXTRUSION"
    generation_method_version: str = "1.0.0"
    vuid_algorithm_version: str = "v1"
    predecessor_vuid: Optional[str] = None
    evidence_sources: list[dict] = field(default_factory=list)
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
