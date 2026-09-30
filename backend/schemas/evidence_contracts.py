from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.domain.enums import EvidenceType


class EvidenceRegisterRequest(BaseModel):
    id: str = Field(..., min_length=2, max_length=64, description="Unique evidence ID (e.g. EVID-001)")
    parent_ulpin: str = Field(..., pattern=r"^[0-9]{14}$")
    evidence_type: EvidenceType
    provider: str = Field(..., min_length=1)
    source_reference: str = Field(..., min_length=1)
    checksum: str = Field(..., min_length=8, description="Cryptographic SHA-256 or reference checksum")
    crs: Optional[str] = None
    acquisition_time: Optional[datetime] = None
    processing_version: str = "1.0.0"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceResponse(BaseModel):
    id: str
    parent_ulpin: str
    evidence_type: str
    provider: str
    source_reference: str
    checksum: str
    crs: Optional[str]
    acquisition_time: Optional[datetime]
    processing_version: str
    metadata: dict[str, Any]
    quality_status: str = "ACCEPTED"
    quality_notes: list[str] = Field(default_factory=list)
    is_duplicate: bool = False
    duplicate_of_id: Optional[str] = None
    is_stale: bool = False
    created_at: datetime


class EvidenceConflict(BaseModel):
    source_a_id: str
    source_b_id: str
    parameter: str
    source_a_value: Any
    source_b_value: Any
    discrepancy: str
    level_code: Optional[str] = None
    resolution_status: str = "PENDING_HUMAN_RESOLUTION"


class EvidenceQualityReport(BaseModel):
    evidence_id: str
    parent_ulpin: str
    status: str  # ACCEPTED, WARNING, BLOCKED
    checks_evaluated: int
    passed_checks: list[str]
    warnings: list[str]
    blockers: list[str]

