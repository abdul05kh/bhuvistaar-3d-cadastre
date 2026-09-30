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
        raise UnitNotFoundError(vuid)

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
