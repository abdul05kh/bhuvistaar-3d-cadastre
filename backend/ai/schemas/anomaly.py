from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from backend.domain.enums import AnomalyType, IssueSeverity
from backend.ai.schemas.candidate import ModelMetadata


class AIAnomaly(BaseModel):
    anomaly_id: str = Field(..., description="Unique anomaly identifier (e.g. anom-uuid)")
    parent_ulpin: str = Field(..., max_length=14, description="Parent parcel 14-digit ULPIN")
    anomaly_type: AnomalyType = Field(..., description="Classification of detected anomaly")
    severity: IssueSeverity = Field(..., description="Operational severity: INFO, WARN, ERROR, BLOCKER")
    affected_units: list[str] = Field(default_factory=list, description="Identifiers of candidate units or level codes affected")
    evidence_ids: list[str] = Field(default_factory=list, description="Supporting or conflicting evidence IDs")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    reason_codes: list[str] = Field(default_factory=list, description="Detailed explanatory reason codes")
    recommended_action: str = Field(..., description="Recommended human reviewer action")
    model: ModelMetadata = Field(..., description="Detecting model or engine details")
    resolved: bool = Field(default=False, description="Whether the anomaly has been resolved")
    resolution_notes: Optional[str] = Field(default=None, description="Notes documenting resolution")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "anomaly_id": "anom-001",
                "parent_ulpin": "12345678901234",
                "anomaly_type": "OVERLAPPING_LEVELS",
                "severity": "BLOCKER",
                "affected_units": ["L01", "L02"],
                "evidence_ids": ["EVID-003"],
                "confidence": 0.98,
                "reason_codes": ["VERTICAL_EXTENT_OVERLAP"],
                "recommended_action": "INSPECT: Reconcile vertical stratum boundaries between Level 1 and Level 2",
                "model": {
                    "name": "cadastral-anomaly-001",
                    "version": "0.1.0"
                }
            }
        }
    }
