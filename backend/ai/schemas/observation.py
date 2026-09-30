import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field
from backend.domain.enums import ObservationType, ExtractionMethod


class EvidenceObservation(BaseModel):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4)
    evidence_id: str = Field(..., description="ID of source evidence record in evidence_sources table")
    parent_ulpin: str = Field(..., max_length=14, description="Parent parcel 14-digit ULPIN")
    observation_type: ObservationType = Field(..., description="Type of extracted observation")
    semantic_level: Optional[str] = Field(default=None, description="Inferred semantic floor level, e.g. L01, L02")
    z_min: Optional[float] = Field(default=None, description="Observed lower elevation bound in metres")
    z_max: Optional[float] = Field(default=None, description="Observed upper elevation bound in metres")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score (0.0 to 1.0)")
    source_reference: str = Field(..., description="Reference within source evidence, e.g. drawing sheet, sheet section")
    extraction_method: ExtractionMethod = Field(..., description="Method used to extract this observation")
    extraction_version: str = Field(default="1.0.0", description="Version of the extraction pipeline")
    model_name: str = Field(..., description="Name of the model or extractor")
    model_version: str = Field(..., description="Version of the model or extractor")
    geometry_geojson: Optional[dict[str, Any]] = Field(default=None, description="Optional 2D/3D geometry of the observation")
    input_checksum: str = Field(..., description="SHA-256 checksum of source evidence input")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional contextual metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "evidence_id": "EVID-003",
                "parent_ulpin": "12345678901234",
                "observation_type": "FLOOR_BOUNDARY",
                "semantic_level": "L01",
                "z_min": 103.0,
                "z_max": 106.0,
                "confidence": 0.94,
                "source_reference": "Drawing Plan Section A-A",
                "extraction_method": "HEURISTIC_CAD_EXTRACTOR",
                "model_name": "evidence-extractor-001",
                "model_version": "0.1.0",
                "input_checksum": "a" * 64
            }
        }
    }
