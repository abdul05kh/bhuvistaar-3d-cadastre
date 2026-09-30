from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from backend.db.models import SpatialUnitRevisionModel, SpatialUnitModel
from backend.domain.revision import SpatialUnitRevision
from backend.domain.enums import SemanticType, UnitStatus
from backend.config import settings


class RevisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, revision: SpatialUnitRevision) -> SpatialUnitRevision:
        if not hasattr(self.db, "add"):
            return revision
        geom_element = from_shape(revision.footprint_geom, srid=settings.CANONICAL_STORAGE_SRID)
        model = SpatialUnitRevisionModel(
            id=revision.id,
            unit_id=revision.unit_id,
            revision_number=revision.revision_number,
            prototype_vuid=revision.prototype_vuid,
            parent_ulpin=revision.parent_ulpin,
            semantic_type=revision.semantic_type.value,
            level_code=revision.level_code,
            z_min=revision.z_min,
            z_max=revision.z_max,
            footprint_area_sqm=revision.footprint_area_sqm,
            volume_cbm=revision.volume_cbm,
            centroid_x=revision.centroid_x,
            centroid_y=revision.centroid_y,
            centroid_z=revision.centroid_z,
            footprint_geom=geom_element,
            polyhedron_wkt=revision.polyhedron_wkt,
            vuid_full_hash=revision.vuid_full_hash,
            predecessor_revision_id=revision.predecessor_revision_id,
            status=revision.status.value,
            created_by=revision.created_by,
            created_at=revision.created_at
        )
        self.db.add(model)
        self.db.flush()
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, revision_id: UUID) -> Optional[SpatialUnitRevision]:
        model = self.db.query(SpatialUnitRevisionModel).filter_by(id=revision_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_unit_id(self, unit_id: UUID) -> list[SpatialUnitRevision]:
        models = (
            self.db.query(SpatialUnitRevisionModel)
            .filter_by(unit_id=unit_id)
            .order_by(SpatialUnitRevisionModel.revision_number.asc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_parent_ulpin(self, ulpin: str) -> list[SpatialUnitRevision]:
        models = (
            self.db.query(SpatialUnitRevisionModel)
            .filter_by(parent_ulpin=ulpin)
            .order_by(SpatialUnitRevisionModel.created_at.asc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_latest_for_unit(self, unit_id: UUID) -> Optional[SpatialUnitRevision]:
        model = (
            self.db.query(SpatialUnitRevisionModel)
            .filter_by(unit_id=unit_id)
            .order_by(SpatialUnitRevisionModel.revision_number.desc())
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def update_status(self, revision_id: UUID, status: UnitStatus) -> Optional[SpatialUnitRevision]:
        model = self.db.query(SpatialUnitRevisionModel).filter_by(id=revision_id).first()
        if not model:
            return None
        model.status = status.value
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, model: SpatialUnitRevisionModel) -> SpatialUnitRevision:
        return SpatialUnitRevision(
            id=model.id,
            unit_id=model.unit_id,
            revision_number=model.revision_number,
            prototype_vuid=model.prototype_vuid,
            parent_ulpin=model.parent_ulpin,
            semantic_type=SemanticType(model.semantic_type),
            level_code=model.level_code,
            z_min=float(model.z_min),
            z_max=float(model.z_max),
            footprint_area_sqm=float(model.footprint_area_sqm),
            volume_cbm=float(model.volume_cbm),
            centroid_x=float(model.centroid_x),
            centroid_y=float(model.centroid_y),
            centroid_z=float(model.centroid_z),
            footprint_geom=to_shape(model.footprint_geom),
            polyhedron_wkt=model.polyhedron_wkt,
            vuid_full_hash=model.vuid_full_hash,
            predecessor_revision_id=model.predecessor_revision_id,
            status=UnitStatus(model.status),
            created_by=model.created_by,
            created_at=model.created_at
        )
