from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from backend.db.session import get_db
from backend.repository.unit_repository import SpatialUnitRepository
from backend.schemas.unit_contracts import SpatialUnitResponse
from backend.schemas.common import GeoJSONPolygon
from backend.exceptions import UnitNotFoundError


router = APIRouter(prefix="/units", tags=["Units"])


@router.get("/{vuid}", response_model=SpatialUnitResponse)
def get_spatial_unit(vuid: str, db: Session = Depends(get_db)):
    repo = SpatialUnitRepository(db)
    u = repo.find_by_vuid(vuid)
    if not u:
        from backend.db.models import SpatialUnitRevisionModel
        from geoalchemy2.shape import to_shape
        rev_match = db.query(SpatialUnitRevisionModel).filter_by(prototype_vuid=vuid).first()
        if not rev_match:
            raise UnitNotFoundError(vuid)
        
        footprint_poly = to_shape(rev_match.footprint_geom)
        geom_dict = mapping(footprint_poly)
        return SpatialUnitResponse(
            id=str(rev_match.unit_id),
            prototype_vuid=rev_match.prototype_vuid,
            parent_ulpin=rev_match.parent_ulpin,
            semantic_type=rev_match.semantic_type,
            level_code=rev_match.level_code,
            z_min=rev_match.z_min,
            z_max=rev_match.z_max,
            height_m=round(rev_match.z_max - rev_match.z_min, 3),
            footprint_area_sqm=rev_match.footprint_area_sqm,
            volume_cbm=rev_match.volume_cbm,
            centroid_x=rev_match.centroid_x,
            centroid_y=rev_match.centroid_y,
            centroid_z=rev_match.centroid_z,
            confidence="VERIFIED",
            generation_method="PRISMATIC_EXTRUSION",
            vuid_algorithm_version="v1",
            vuid_full_hash=rev_match.vuid_full_hash,
            source_ids=[],
            status=rev_match.status,
            footprint_geom=GeoJSONPolygon(type="Polygon", coordinates=geom_dict["coordinates"]),
            polyhedron_wkt=rev_match.polyhedron_wkt,
            created_at=rev_match.created_at
        )

    geom_dict = mapping(u.footprint_geom)
    return SpatialUnitResponse(
        id=str(u.id),
        prototype_vuid=u.prototype_vuid,
        parent_ulpin=u.parent_ulpin,
        semantic_type=u.semantic_type.value,
        level_code=u.level_code,
        z_min=u.z_min,
        z_max=u.z_max,
        height_m=u.height_m,
        footprint_area_sqm=u.footprint_area_sqm,
        volume_cbm=u.volume_cbm,
        centroid_x=u.centroid_x,
        centroid_y=u.centroid_y,
        centroid_z=u.centroid_z,
        confidence=u.confidence.value,
        generation_method=u.generation_method,
        vuid_algorithm_version=u.vuid_algorithm_version,
        vuid_full_hash=u.vuid_full_hash,
        source_ids=u.source_ids,
        status=u.status.value,
        footprint_geom=GeoJSONPolygon(type="Polygon", coordinates=geom_dict["coordinates"]),
        polyhedron_wkt=u.polyhedron_wkt,
        created_at=u.created_at
    )


@router.get("/{vuid}/revisions")
def list_revisions(vuid: str, db: Session = Depends(get_db)):
    from backend.repository.revision_repository import RevisionRepository
    from backend.db.models import SpatialUnitRevisionModel
    unit_repo = SpatialUnitRepository(db)
    u = unit_repo.find_by_vuid(vuid)
    if u:
        unit_id = u.id
    else:
        # Check historical revision table
        rev_match = db.query(SpatialUnitRevisionModel).filter_by(prototype_vuid=vuid).first()
        if not rev_match:
            raise UnitNotFoundError(vuid)
        unit_id = rev_match.unit_id

    rev_repo = RevisionRepository(db)
    revisions = rev_repo.find_by_unit_id(unit_id)
    return [
        {
            "id": str(r.id),
            "revision_number": r.revision_number,
            "prototype_vuid": r.prototype_vuid,
            "level_code": r.level_code,
            "z_min": r.z_min,
            "z_max": r.z_max,
            "status": r.status.value,
            "predecessor_revision_id": str(r.predecessor_revision_id) if r.predecessor_revision_id else None,
            "created_by": r.created_by,
            "created_at": r.created_at.isoformat()
        }
        for r in revisions
    ]

