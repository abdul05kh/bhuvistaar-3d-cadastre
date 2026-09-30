from typing import Any, Optional
from pydantic import BaseModel, Field


class TraceOriginNode(BaseModel):
    step: int = Field(..., description="Chronological sequence index")
    stage: str = Field(..., description="Stage in the cadastral lifecycle (EVIDENCE, INFERENCE, CANDIDATE, VALIDATION, REVIEW, REVISION, GATE_C, EXPORT)")
    title: str = Field(..., description="Stage title")
    identifier: str = Field(..., description="Record primary identifier (e.g. EVID-003, cand-001, vuid-...)")
    status: str = Field(..., description="Operational status at this stage")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp")
    actor: str = Field(..., description="Actor / Engine responsible (e.g. AI:prismatic-001, SYSTEM_VALIDATOR, officer_01)")
    details: dict[str, Any] = Field(default_factory=dict, description="Structured factual metadata")


class TraceOriginResponse(BaseModel):
    target_identifier: str = Field(..., description="Target candidate_id or prototype_vuid")
    parent_ulpin: str = Field(..., description="Parent parcel ULPIN")
    lineage_path: list[TraceOriginNode] = Field(default_factory=list, description="Ordered traversal path")
    is_authoritative: bool = Field(default=False, description="Whether this unit has attained governed approval")
    provenance_hash: Optional[str] = Field(default=None, description="Checksum or VUID hash")
