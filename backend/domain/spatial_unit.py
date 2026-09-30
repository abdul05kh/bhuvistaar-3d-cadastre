from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from shapely.geometry import Polygon
from backend.domain.enums import SemanticType, ConfidenceLevel, UnitStatus


@dataclass
class SpatialUnit3D:
    parent_parcel_id: UUID
    parent_ulpin: str
    prototype_vuid: str
    semantic_type: SemanticType
    level_code: str
    z_min: float
    z_max: float
    footprint_area_sqm: float
    volume_cbm: float
    centroid_x: float
    centroid_y: float
    centroid_z: float
    footprint_geom: Polygon
    vuid_full_hash: str
    source_ids: list[str] = field(default_factory=list)
    generation_method: str = "PRISMATIC_EXTRUSION"
    vuid_algorithm_version: str = "v1"
    polyhedron_wkt: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    status: UnitStatus = UnitStatus.GENERATED
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def height_m(self) -> float:
        return round(self.z_max - self.z_min, 3)

    def __post_init__(self):
        if self.z_min >= self.z_max:
            raise ValueError(f"z_min ({self.z_min}) must be strictly less than z_max ({self.z_max})")
        if not self.prototype_vuid.startswith(f"BV-{self.parent_ulpin}-"):
            raise ValueError(f"Prototype VUID '{self.prototype_vuid}' must begin with 'BV-{self.parent_ulpin}-'")
