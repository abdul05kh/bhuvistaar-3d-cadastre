from sqlalchemy.orm import Session
from shapely.geometry import shape, Polygon
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.enums import UnitStatus, ConfidenceLevel
from backend.schemas.unit_contracts import UnitGenerateRequest
from backend.repository.parcel_repository import ParcelRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.evidence_repository import EvidenceRepository
from backend.geometry.extrusion import compute_volumetric_extrusion
from backend.geometry.topology import check_polygon_validity, check_finite_coordinates
from backend.vuid.generator import generate_prototype_vuid
from backend.exceptions import ParcelNotFoundError, InvalidGeometryError, EvidenceNotFoundError


class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.parcel_repo = ParcelRepository(db)
        self.unit_repo = SpatialUnitRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        from backend.repository.revision_repository import RevisionRepository
        from backend.services.provenance_service import ProvenanceService
        from backend.services.audit_service import AuditService
        from backend.domain.revision import SpatialUnitRevision
        from backend.domain.enums import AuditAction

        self.revision_repo = RevisionRepository(db)
        self.prov_service = ProvenanceService(db)
        self.audit_service = AuditService(db)

    def generate_3d_units(self, ulpin: str, request: UnitGenerateRequest) -> list[SpatialUnit3D]:
        parcel = self.parcel_repo.find_by_ulpin(ulpin)
        if not parcel:
            raise ParcelNotFoundError(ulpin)

        # Verify evidence IDs exist
        for eid in request.evidence_ids:
            ev = self.evidence_repo.find_by_id(eid)
            if not ev:
                raise EvidenceNotFoundError(eid)

        # Parse footprint
        footprint_poly = shape(request.footprint.model_dump())
        if not isinstance(footprint_poly, Polygon):
            raise InvalidGeometryError("Building footprint must be a Polygon.")

        finite_ok, finite_err = check_finite_coordinates(footprint_poly)
        if not finite_ok:
            raise InvalidGeometryError(f"Footprint coordinate error: {finite_err}")

        valid_ok, valid_err = check_polygon_validity(footprint_poly)
        if not valid_ok:
            raise InvalidGeometryError(f"Footprint topology error: {valid_err}")

        # Note: We do NOT clip footprint to parcel here (Rule TOP-001 checks containment deterministically)

        generated_units: list[SpatialUnit3D] = []

        from backend.domain.revision import SpatialUnitRevision
        from backend.domain.enums import AuditAction

        for floor in request.floors:
            # 1. Volumetric metrics (area, height, volume, centroid, 3D polyhedron)
            metrics = compute_volumetric_extrusion(
                polygon=footprint_poly,
                z_min=floor.z_min,
                z_max=floor.z_max
            )

            # 2. Deterministic Prototype VUID calculation
            vuid_res = generate_prototype_vuid(
                parent_ulpin=ulpin,
                unit_class="BLDG",
                level_code=floor.level,
                footprint_geom=footprint_poly,
                z_min=floor.z_min,
                z_max=floor.z_max
            )

            # 3. Create domain SpatialUnit3D
            unit = SpatialUnit3D(
                parent_parcel_id=parcel.id,
                parent_ulpin=ulpin,
                prototype_vuid=vuid_res.prototype_vuid,
                semantic_type=floor.semantic_type,
                level_code=floor.level,
                z_min=floor.z_min,
                z_max=floor.z_max,
                footprint_area_sqm=metrics.footprint_area_sqm,
                volume_cbm=metrics.volume_cbm,
                centroid_x=metrics.centroid_x,
                centroid_y=metrics.centroid_y,
                centroid_z=metrics.centroid_z,
                footprint_geom=footprint_poly,
                polyhedron_wkt=metrics.polyhedron_wkt,
                confidence=ConfidenceLevel.VERIFIED,
                generation_method="PRISMATIC_EXTRUSION",
                vuid_algorithm_version=vuid_res.vuid_algorithm_version,
                vuid_full_hash=vuid_res.vuid_full_hash,
                source_ids=request.evidence_ids,
                status=UnitStatus.GENERATED
            )

            saved_unit = self.unit_repo.save(unit)

            # 4. Create Revision 1 for this spatial unit
            revision_1 = SpatialUnitRevision(
                unit_id=saved_unit.id,
                revision_number=1,
                prototype_vuid=saved_unit.prototype_vuid,
                parent_ulpin=ulpin,
                semantic_type=saved_unit.semantic_type,
                level_code=saved_unit.level_code,
                z_min=saved_unit.z_min,
                z_max=saved_unit.z_max,
                footprint_area_sqm=saved_unit.footprint_area_sqm,
                volume_cbm=saved_unit.volume_cbm,
                centroid_x=saved_unit.centroid_x,
                centroid_y=saved_unit.centroid_y,
                centroid_z=saved_unit.centroid_z,
                footprint_geom=saved_unit.footprint_geom,
                polyhedron_wkt=saved_unit.polyhedron_wkt,
                vuid_full_hash=saved_unit.vuid_full_hash,
                status=UnitStatus.GENERATED,
                created_by="SYSTEM"
            )
            saved_rev = self.revision_repo.save(revision_1)
            self.unit_repo.set_active_revision(saved_unit.id, saved_rev.id)

            # 5. Create structured ProvenanceRecord
            self.prov_service.ev_repo = self.evidence_repo
            self.prov_service.create_provenance(
                revision=saved_rev,
                evidence_ids=request.evidence_ids,
                generation_method="PRISMATIC_EXTRUSION",
                generation_method_version="1.0.0",
                vuid_algorithm_version=vuid_res.vuid_algorithm_version
            )

            # 6. Audit Events
            self.audit_service.log_event(
                action=AuditAction.CANDIDATE_CREATED,
                entity_type="SPATIAL_UNIT",
                entity_id=saved_unit.prototype_vuid,
                revision_id=saved_rev.id,
                new_state=UnitStatus.GENERATED.value,
                reason="Candidate 3D spatial unit generated via prismatic extrusion."
            )
            self.audit_service.log_event(
                action=AuditAction.REVISION_CREATED,
                entity_type="SPATIAL_UNIT_REVISION",
                entity_id=str(saved_rev.id),
                revision_id=saved_rev.id,
                new_state=UnitStatus.GENERATED.value,
                reason=f"Initial candidate Revision 1 created with prototype VUID {saved_unit.prototype_vuid}."
            )

            generated_units.append(saved_unit)

        return generated_units

