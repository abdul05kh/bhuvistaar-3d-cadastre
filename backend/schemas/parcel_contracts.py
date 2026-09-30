from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from backend.schemas.common import GeoJSONPolygon


class ParcelIngestRequest(BaseModel):
    ulpin: str = Field(..., pattern=r"^[0-9]{14}$", description="14-digit immutable parent ULPIN")
    crs: str = Field(..., min_length=4, max_length=32, description="Source Coordinate Reference System (e.g., EPSG:32643)")
    geometry: GeoJSONPolygon
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ulpin")
    @classmethod
    def validate_ulpin(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 14:
            raise ValueError("ULPIN must be exactly 14 numeric digits.")
        return v


class ParcelResponse(BaseModel):
    id: str
    ulpin: str
    crs: str
    storage_srid: int
    area_sqm: float
    status: str
    geometry: GeoJSONPolygon
    metadata: dict[str, Any]
    created_at: datetime
