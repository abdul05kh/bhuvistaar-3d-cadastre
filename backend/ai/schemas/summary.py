from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from backend.domain.enums import IssueSeverity


class AIAssistanceSummary(BaseModel):
    parent_ulpin: str = Field(..., max_length=14, description="Parent parcel 14-digit ULPIN")
    total_candidates: int = Field(default=0, description="Total AI proposals generated")
    high_confidence_count: int = Field(default=0, description="Candidates with confidence >= 0.85")
    medium_confidence_count: int = Field(default=0, description="Candidates with confidence 0.60 - 0.849")
    low_confidence_count: int = Field(default=0, description="Candidates with confidence < 0.60")
    anomalies_count: int = Field(default=0, description="Total detected anomalies")
    blocker_count: int = Field(default=0, description="Blocker issues preventing approval")
    evidence_conflicts_count: int = Field(default=0, description="Discrepant evidence conflicts detected")
    review_required_count: int = Field(default=0, description="Items awaiting officer review")
    model_name: str = Field(default="prismatic-candidate-001")
    model_version: str = Field(default="0.1.0")
    inference_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operational_disclaimer: str = Field(
        default="AI proposals are candidate-only; deterministic spatial validation and human governance remain mandatory.",
        description="Mandatory disclaimer banner"
    )


class ReviewerQueueItem(BaseModel):
    priority: int = Field(..., description="1=Blocker/Immediate, 2=Anomaly/High, 3=Low Confidence, 4=Standard Candidate")
    item_type: str = Field(..., description="BLOCKER, ANOMALY, CANDIDATE_REVIEW")
    identifier: str = Field(..., description="Candidate ID or Anomaly ID")
    title: str = Field(..., description="Short descriptive title")
    severity: IssueSeverity = Field(..., description="Severity level")
    confidence: Optional[float] = Field(default=None, description="Confidence if candidate/anomaly")
    reason: str = Field(..., description="Reason for flagging")
    recommended_action: str = Field(..., description="Actionable recommendation for human reviewer")
    affected_level: Optional[str] = Field(default=None, description="Floor level, e.g. L01")


class ReviewerQueueResponse(BaseModel):
    parent_ulpin: str = Field(...)
    total_items: int = Field(default=0)
    items: list[ReviewerQueueItem] = Field(default_factory=list)


class FactBasedExplanationResponse(BaseModel):
    target_id: str = Field(..., description="Target candidate or unit ID")
    target_type: str = Field(..., description="CANDIDATE, SPATIAL_UNIT, ANOMALY")
    summary: str = Field(..., description="Clear factual summary")
    evidence_basis: list[str] = Field(default_factory=list, description="Evidence items supporting or conflicting")
    geometric_facts: list[str] = Field(default_factory=list, description="Verified geometric measurements")
    validation_status: str = Field(..., description="PASS, FAIL, BLOCKER, PENDING")
    governance_status: str = Field(..., description="AI_CANDIDATE, UNDER_REVIEW, APPROVED, REJECTED")
    disclaimer: str = Field(
        default="Explanation synthesized strictly from structured topological and provenance facts. No generative hallucination.",
        description="Grounding disclaimer"
    )
