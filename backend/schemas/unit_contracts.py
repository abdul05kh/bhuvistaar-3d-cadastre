from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from backend.domain.enums import SemanticType, ConfidenceLevel, UnitStatus
from backend.schemas.common import GeoJSONPolygon


class FloorSliceInput(BaseModel):
    level: str = Field(..., pattern=r"^(B[1-9]|G|L0[1-9]|L[1-9][0-9])$", description="Level code (e.g. B1, G, L01, L02)")
    z_min: float = Field(..., description="Bottom vertical boundary in metres")
    z_max: float = Field(..., description="Top vertical boundary in metres")
    semantic_type: SemanticType = Field(default=SemanticType.FLOOR_VOLUME)

    @model_validator(mode="after")
    def check_z_order(self) -> "FloorSliceInput":
        if self.z_min >= self.z_max:
            raise ValueError(f"z_min ({self.z_min}) must be strictly less than z_max ({self.z_max})")
        return self


class UnitGenerateRequest(BaseModel):
    building_id: str = Field(default="BLDG-001", description="Identifier of the building mass")
    footprint: GeoJSONPolygon = Field(..., description="2D footprint polygon in parcel coordinates")
    floors: list[FloorSliceInput] = Field(..., min_length=1, description="List of vertical floor strata")
    evidence_ids: list[str] = Field(..., min_length=1, description="IDs of evidence supporting this unit derivation")


class SpatialUnitResponse(BaseModel):
    id: str
    prototype_vuid: str
    parent_ulpin: str
    semantic_type: str
    level_code: str
    z_min: float
    z_max: float
    height_m: float
    footprint_area_sqm: float
    volume_cbm: float
    centroid_x: float
    centroid_y: float
    centroid_z: float
    confidence: str
    generation_method: str
    vuid_algorithm_version: str
    vuid_full_hash: str
    source_ids: list[str]
    status: str
    footprint_geom: GeoJSONPolygon
    polyhedron_wkt: Optional[str]
    created_at: datetime
