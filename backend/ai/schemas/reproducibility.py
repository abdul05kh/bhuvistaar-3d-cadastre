"""Reproducibility Snapshot Schemas (Slice 4)."""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.domain.enums import ReproducibilityStatus


class ReproducibilitySnapshotResponse(BaseModel):
    snapshot_id: str
    parent_ulpin: str
    target_type: str
    target_id: str
    revision_id: Optional[str] = None
    reproducibility_status: ReproducibilityStatus
    input_evidence_hashes: list[str] = Field(default_factory=list)
    geometry_geojson: dict[str, Any] = Field(default_factory=dict)
    crs: str
    generation_method: str
    model: dict[str, str] = Field(default_factory=dict)
    model_config_hash: str
    validation_ruleset_version: str = "1.0.0"
    software_commit: str
    snapshot_hash: str
    can_reproduce: bool
    verification_report: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class ReproducibilityVerificationRequest(BaseModel):
    target_id: str
    recompute_hash: bool = True
