from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from backend.domain.enums import ReviewDecisionType, ApprovalStatus


class ReviewSubmitRequest(BaseModel):
    decision: ReviewDecisionType = Field(..., description="Review outcome: ACCEPT, REQUEST_CORRECTION, or REJECT")
    reason: str = Field(..., min_length=3, description="Officer's review justification or correction instructions")
    reviewer_id: str = Field(default="OFFICER-001", description="Reviewer/officer identifier")
    actor_context: str = Field(default="SIMULATED_PROTOTYPE", description="Simulated prototype actor context")


class ReviewDecisionResponse(BaseModel):
    id: str
    revision_id: str
    reviewer_id: str
    decision: str
    reason: str
    actor_context: str
    referenced_validation_run_id: Optional[str] = None
    created_at: datetime


class CorrectionSubmitRequest(BaseModel):
    reviewer_id: str = Field(default="OFFICER-001", description="Reviewer/officer requesting and applying correction")
    reason: str = Field(..., min_length=3, description="Detailed explanation of the geometric or attribute correction")
    z_min: Optional[float] = Field(None, description="Corrected lower elevation boundary in metres")
    z_max: Optional[float] = Field(None, description="Corrected upper elevation boundary in metres")
    footprint: Optional[dict] = Field(None, description="Corrected GeoJSON Polygon footprint")
    semantic_type: Optional[str] = Field(None, description="Corrected semantic unit classification")
    actor_context: str = Field(default="SIMULATED_PROTOTYPE", description="Simulated prototype actor context")


class CorrectionResponse(BaseModel):
    new_revision_id: str
    predecessor_revision_id: str
    prototype_vuid: str
    vuid_full_hash: str
    validation_run_id: str
    blocker_count: int
    can_approve: bool
    status: str
    created_at: datetime


class ApprovalSubmitRequest(BaseModel):
    approver_id: str = Field(default="OFFICER-001", description="Approving officer identifier")
    reason: str = Field(..., min_length=3, description="Approval justification and compliance determination")
    actor_context: str = Field(default="SIMULATED_PROTOTYPE", description="Simulated prototype actor context")
    role: Optional[str] = Field(None, description="Operational role of actor (e.g. APPROVER, ADMIN, VIEWER, REVIEWER)")


class ApprovalDecisionResponse(BaseModel):
    id: str
    revision_id: str
    approver_id: str
    status: str
    reason: str
    referenced_validation_run_id: str
    referenced_review_id: str
    actor_context: str
    created_at: datetime


class RejectionSubmitRequest(BaseModel):
    actor_id: str = Field(default="OFFICER-001", description="Rejecting officer identifier")
    reason: str = Field(..., min_length=3, description="Rejection rationale")
    actor_context: str = Field(default="SIMULATED_PROTOTYPE", description="Simulated prototype actor context")


class RejectionResponse(BaseModel):
    revision_id: str
    status: str
    reason: str
    created_at: datetime


class AuditEventResponse(BaseModel):
    id: str
    timestamp: datetime
    actor_id: str
    authorization_mode: str
    action: str
    entity_type: str
    entity_id: str
    revision_id: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StructuredExportResponse(BaseModel):
    export_metadata: dict[str, Any]
    parcel: dict[str, Any]
    parent_ulpin: str
    spatial_unit: dict[str, Any]
    spatial_unit_revision: dict[str, Any]
    vuid: dict[str, Any]
    geometry: dict[str, Any]
    elevation: dict[str, Any]
    evidence: list[dict[str, Any]]
    provenance: dict[str, Any]
    validation: dict[str, Any]
    review: Optional[dict[str, Any]] = None
    approval: Optional[dict[str, Any]] = None
    audit_summary: dict[str, Any]
