from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Polygon
from backend.db.models import ParentParcelModel
from backend.domain.parcel import ParentParcel
from backend.domain.enums import UnitStatus
from backend.config import settings


class ParcelRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, parcel: ParentParcel) -> ParentParcel:
        geom_element = from_shape(parcel.geometry, srid=settings.CANONICAL_STORAGE_SRID)
        model = self.db.query(ParentParcelModel).filter_by(ulpin=parcel.ulpin).first()
        
        if model:
            model.geometry = geom_element
            model.area_sqm = parcel.area_sqm
            model.status = parcel.status.value
            model.metadata_json = parcel.metadata
            model.updated_at = parcel.updated_at
        else:
            model = ParentParcelModel(
                id=parcel.id,
                ulpin=parcel.ulpin,
                crs=parcel.crs,
                storage_srid=settings.CANONICAL_STORAGE_SRID,
                geometry=geom_element,
                area_sqm=parcel.area_sqm,
                status=parcel.status.value,
                metadata_json=parcel.metadata,
                created_at=parcel.created_at,
                updated_at=parcel.updated_at
            )
            self.db.add(model)
            
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_ulpin(self, ulpin: str) -> Optional[ParentParcel]:
        model = self.db.query(ParentParcelModel).filter_by(ulpin=ulpin).first()
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: ParentParcelModel) -> ParentParcel:
        shapely_poly = to_shape(model.geometry)
        return ParentParcel(
            id=model.id,
            ulpin=model.ulpin,
            crs=model.crs,
            storage_srid=model.storage_srid,
            geometry=shapely_poly,
            area_sqm=float(model.area_sqm),
            status=UnitStatus(model.status),
            metadata=model.metadata_json or {},
            created_at=model.created_at,
            updated_at=model.updated_at
        )
