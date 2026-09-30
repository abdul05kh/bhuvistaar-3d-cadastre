from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from backend.domain.enums import SemanticType, CandidateStatus, ReasonCode
from backend.config import settings


class VerticalExtent(BaseModel):
    z_min: float = Field(..., description="Bottom floor elevation in metres")
    z_max: float = Field(..., description="Top floor elevation in metres")

    @model_validator(mode="after")
    def validate_vertical_bounds(self) -> "VerticalExtent":
        if self.z_max <= self.z_min:
            raise ValueError(f"z_max ({self.z_max}m) must be strictly greater than z_min ({self.z_min}m)")
        return self


class ModelMetadata(BaseModel):
    name: str = Field(..., description="Model identifier")
    version: str = Field(..., description="Model semantic version")


class CandidateSpatialUnit(BaseModel):
    candidate_id: str = Field(..., description="Unique AI candidate identifier (e.g. cand-uuid)")
    parent_ulpin: str = Field(..., max_length=14, description="Parent parcel 14-digit ULPIN")
    source_evidence_ids: list[str] = Field(default_factory=list, description="IDs of source evidence records supporting this proposal")
    geometry: dict[str, Any] = Field(..., description="2D footprint geometry as GeoJSON Polygon")
    vertical_extent: VerticalExtent = Field(..., description="Vertical bounds [z_min, z_max] in metres")
    semantic_type: SemanticType = Field(default=SemanticType.FLOOR_VOLUME, description="Semantic classification")
    level_code: str = Field(..., description="Semantic level tag, e.g. B1, Ground, L01, L02")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score (0.0 to 1.0)")
    confidence_band: str = Field(..., description="Operational policy threshold: HIGH, MEDIUM, LOW")
    reason_codes: list[str] = Field(default_factory=list, description="Transparent explainability reason codes")
    model: ModelMetadata = Field(..., description="Generating model name and version")
    status: CandidateStatus = Field(default=CandidateStatus.AI_CANDIDATE, description="Lifecycle status")
    
    # Computed metrics
    footprint_area_sqm: float = Field(..., gt=0.0, description="Planar area in square metres")
    volume_cbm: float = Field(..., gt=0.0, description="Extruded 3D volume in cubic metres")
    centroid_x: float = Field(..., description="Centroid X in canonical projected CRS")
    centroid_y: float = Field(..., description="Centroid Y in canonical projected CRS")
    centroid_z: float = Field(..., description="Centroid Z elevation in metres")
    
    # Governance linkage
    governed_unit_id: Optional[str] = Field(default=None, description="Linked spatial unit ID once accepted")
    governed_revision_id: Optional[str] = Field(default=None, description="Linked spatial unit revision ID once accepted")
    rejection_reason: Optional[str] = Field(default=None, description="Reviewer justification if rejected")
    reviewed_by: Optional[str] = Field(default=None, description="Reviewer identifier")
    reviewed_at: Optional[datetime] = Field(default=None, description="Review timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("status")
    @classmethod
    def validate_never_approved(cls, v: CandidateStatus) -> CandidateStatus:
        if v == "APPROVED":
            raise ValueError("CRITICAL GOVERNANCE VIOLATION: AI candidate can never be assigned status APPROVED by AI service.")
        return v

    @field_validator("geometry")
    @classmethod
    def validate_geojson_polygon(cls, v: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(v, dict) or v.get("type") != "Polygon":
            raise ValueError("Geometry must be a GeoJSON Polygon")
        coords = v.get("coordinates")
        if not coords or not isinstance(coords, list) or len(coords[0]) < 4:
            raise ValueError("Polygon must have at least one linear ring with at least 4 coordinates")
        return v

    @classmethod
    def compute_confidence_band(cls, confidence: float) -> str:
        if confidence >= settings.AI_CONFIDENCE_THRESHOLD_HIGH:
            return "HIGH"
        elif confidence >= settings.AI_CONFIDENCE_THRESHOLD_MEDIUM:
            return "MEDIUM"
        return "LOW"


class CandidateReviewRequest(BaseModel):
    reviewer_id: str = Field(default="surveyor_officer_01", description="Reviewer actor identifier")
    justification: str = Field(..., min_length=5, description="Mandatory officer review rationale")


class CandidateCorrectionRequest(BaseModel):
    reviewer_id: str = Field(default="surveyor_officer_01", description="Reviewer actor identifier")
    z_min: Optional[float] = Field(default=None, description="Corrected z_min")
    z_max: Optional[float] = Field(default=None, description="Corrected z_max")
    justification: str = Field(..., min_length=5, description="Mandatory officer correction rationale")
