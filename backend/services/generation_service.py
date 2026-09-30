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
            generated_units.append(saved_unit)

        return generated_units
