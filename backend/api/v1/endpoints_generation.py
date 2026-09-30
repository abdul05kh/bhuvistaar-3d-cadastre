from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from backend.db.session import get_db
from backend.schemas.unit_contracts import UnitGenerateRequest, SpatialUnitResponse
from backend.schemas.common import GeoJSONPolygon
from backend.services.generation_service import GenerationService


router = APIRouter(prefix="/parcels", tags=["Spatial Unit Generation"])


@router.post("/{ulpin}/generate", response_model=list[SpatialUnitResponse], status_code=status.HTTP_201_CREATED)
def generate_spatial_units(
    ulpin: str,
    request: UnitGenerateRequest,
    db: Session = Depends(get_db)
):
    service = GenerationService(db)
    units = service.generate_3d_units(ulpin=ulpin, request=request)
    
    responses: list[SpatialUnitResponse] = []
    for u in units:
        geom_dict = mapping(u.footprint_geom)
        responses.append(
            SpatialUnitResponse(
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
        )
    return responses
