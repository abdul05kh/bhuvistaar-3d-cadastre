from typing import Optional
from uuid import UUID
from shapely.geometry import Polygon
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape, to_shape
from backend.db.models import SpatialUnitModel, unit_evidence_links, EvidenceSourceModel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.enums import SemanticType, ConfidenceLevel, UnitStatus
from backend.exceptions import VUIDCollisionError
from backend.config import settings


class SpatialUnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, unit: SpatialUnit3D) -> SpatialUnit3D:
        existing = self.db.query(SpatialUnitModel).filter_by(prototype_vuid=unit.prototype_vuid).first()
        if existing:
            if existing.vuid_full_hash != unit.vuid_full_hash:
                raise VUIDCollisionError(
                    f"VUID collision detected for '{unit.prototype_vuid}': "
                    f"existing hash {existing.vuid_full_hash} != incoming hash {unit.vuid_full_hash}"
                )
            # Idempotent match: return existing
            return self._to_domain(existing)

        geom_element = from_shape(unit.footprint_geom, srid=settings.CANONICAL_STORAGE_SRID)
        model = SpatialUnitModel(
            id=unit.id,
            prototype_vuid=unit.prototype_vuid,
            parent_parcel_id=unit.parent_parcel_id,
            parent_ulpin=unit.parent_ulpin,
            semantic_type=unit.semantic_type.value,
            level_code=unit.level_code,
            z_min=unit.z_min,
            z_max=unit.z_max,
            footprint_area_sqm=unit.footprint_area_sqm,
            volume_cbm=unit.volume_cbm,
            centroid_x=unit.centroid_x,
            centroid_y=unit.centroid_y,
            centroid_z=unit.centroid_z,
            footprint_geom=geom_element,
            polyhedron_wkt=unit.polyhedron_wkt,
            confidence=unit.confidence.value,
            generation_method=unit.generation_method,
            vuid_algorithm_version=unit.vuid_algorithm_version,
            vuid_full_hash=unit.vuid_full_hash,
            status=unit.status.value,
            created_at=unit.created_at,
            updated_at=unit.updated_at
        )
        self.db.add(model)
        self.db.flush()

        # Link evidence sources
        for eid in unit.source_ids:
            ev_exists = self.db.query(EvidenceSourceModel).filter_by(id=eid).first()
            if ev_exists:
                self.db.execute(
                    unit_evidence_links.insert().values(unit_id=model.id, evidence_id=eid)
                )

        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_vuid(self, vuid: str) -> Optional[SpatialUnit3D]:
        model = self.db.query(SpatialUnitModel).filter_by(prototype_vuid=vuid).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_parent_ulpin(self, ulpin: str) -> list[SpatialUnit3D]:
        models = self.db.query(SpatialUnitModel).filter_by(parent_ulpin=ulpin).order_by(SpatialUnitModel.z_min).all()
        return [self._to_domain(m) for m in models]

    def set_active_revision(self, unit_id: UUID, revision_id: UUID) -> None:
        model = self.db.query(SpatialUnitModel).filter_by(id=unit_id).first()
        if model:
            model.active_revision_id = revision_id
            self.db.commit()

    def update_from_revision(
        self,
        unit_id: UUID,
        revision_id: UUID,
        vuid: str,
        vuid_hash: str,
        footprint: Polygon,
        z_min: float,
        z_max: float,
        status: UnitStatus,
        area_sqm: float,
        volume_cbm: float,
        centroid: tuple[float, float, float]
    ) -> None:
        model = self.db.query(SpatialUnitModel).filter_by(id=unit_id).first()
        if model:
            model.active_revision_id = revision_id
            model.prototype_vuid = vuid
            model.vuid_full_hash = vuid_hash
            model.footprint_geom = from_shape(footprint, srid=settings.CANONICAL_STORAGE_SRID)
            model.z_min = z_min
            model.z_max = z_max
            model.footprint_area_sqm = area_sqm
            model.volume_cbm = volume_cbm
            model.centroid_x = centroid[0]
            model.centroid_y = centroid[1]
            model.centroid_z = centroid[2]
            model.status = status.value
            self.db.commit()


    def _to_domain(self, model: SpatialUnitModel) -> SpatialUnit3D:
        shapely_poly = to_shape(model.footprint_geom)
        
        # Query linked evidence IDs
        links = self.db.execute(
            unit_evidence_links.select().where(unit_evidence_links.c.unit_id == model.id)
        ).fetchall()
        source_ids = [row[1] for row in links]

        return SpatialUnit3D(
            id=model.id,
            parent_parcel_id=model.parent_parcel_id,
            parent_ulpin=model.parent_ulpin,
            prototype_vuid=model.prototype_vuid,
            semantic_type=SemanticType(model.semantic_type),
            level_code=model.level_code,
            z_min=float(model.z_min),
            z_max=float(model.z_max),
            footprint_area_sqm=float(model.footprint_area_sqm),
            volume_cbm=float(model.volume_cbm),
            centroid_x=float(model.centroid_x),
            centroid_y=float(model.centroid_y),
            centroid_z=float(model.centroid_z),
            footprint_geom=shapely_poly,
            polyhedron_wkt=model.polyhedron_wkt,
            confidence=ConfidenceLevel(model.confidence),
            generation_method=model.generation_method,
            vuid_algorithm_version=model.vuid_algorithm_version,
            vuid_full_hash=model.vuid_full_hash,
            source_ids=source_ids,
            status=UnitStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
