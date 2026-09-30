from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from shapely.geometry import Polygon
from backend.domain.enums import UnitStatus


@dataclass
class ParentParcel:
    ulpin: str
    crs: str
    geometry: Polygon
    area_sqm: float
    storage_srid: int = 32643
    id: UUID = field(default_factory=uuid4)
    status: UnitStatus = UnitStatus.DRAFT
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.ulpin or len(self.ulpin) != 14 or not self.ulpin.isdigit():
            raise ValueError(f"Invalid parent ULPIN '{self.ulpin}': must be exactly 14 digits.")
        if self.geometry is None or self.geometry.is_empty:
            raise ValueError("Parent parcel geometry cannot be empty.")
