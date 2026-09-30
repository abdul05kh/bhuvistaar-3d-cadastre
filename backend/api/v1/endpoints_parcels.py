from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from backend.db.session import get_db
from backend.schemas.parcel_contracts import ParcelIngestRequest, ParcelResponse
from backend.schemas.common import GeoJSONPolygon
from backend.services.parcel_service import ParcelService


router = APIRouter(prefix="/parcels", tags=["Parcels"])


@router.post("", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
def ingest_parcel(request: ParcelIngestRequest, db: Session = Depends(get_db)):
    service = ParcelService(db)
    parcel = service.ingest_parcel(request)
    
    geom_dict = mapping(parcel.geometry)
    return ParcelResponse(
        id=str(parcel.id),
        ulpin=parcel.ulpin,
        crs=parcel.crs,
        storage_srid=parcel.storage_srid,
        area_sqm=parcel.area_sqm,
        status=parcel.status.value,
        geometry=GeoJSONPolygon(type="Polygon", coordinates=geom_dict["coordinates"]),
        metadata=parcel.metadata,
        created_at=parcel.created_at
    )


@router.get("/{ulpin}", response_model=ParcelResponse)
def get_parcel(ulpin: str, db: Session = Depends(get_db)):
    service = ParcelService(db)
    parcel = service.get_parcel(ulpin)
    
    geom_dict = mapping(parcel.geometry)
    return ParcelResponse(
        id=str(parcel.id),
        ulpin=parcel.ulpin,
        crs=parcel.crs,
        storage_srid=parcel.storage_srid,
        area_sqm=parcel.area_sqm,
        status=parcel.status.value,
        geometry=GeoJSONPolygon(type="Polygon", coordinates=geom_dict["coordinates"]),
        metadata=parcel.metadata,
        created_at=parcel.created_at
    )


@router.get("/{ulpin}/units")
def get_parcel_units(ulpin: str, db: Session = Depends(get_db)):
    from backend.repository.unit_repository import SpatialUnitRepository
    from backend.repository.revision_repository import RevisionRepository
    from backend.schemas.unit_contracts import SpatialUnitResponse
    
    repo = SpatialUnitRepository(db)
    rev_repo = RevisionRepository(db)
    units = repo.find_by_parent_ulpin(ulpin)
    
    responses = []
    for u in units:
        geom_dict = mapping(u.footprint_geom)
        active_rev = rev_repo.find_latest_for_unit(u.id)
        responses.append({
            "id": str(u.id),
            "prototype_vuid": u.prototype_vuid,
            "parent_ulpin": u.parent_ulpin,
            "semantic_type": u.semantic_type.value,
            "level_code": u.level_code,
            "z_min": u.z_min,
            "z_max": u.z_max,
            "height_m": u.height_m,
            "footprint_area_sqm": u.footprint_area_sqm,
            "volume_cbm": u.volume_cbm,
            "centroid_x": u.centroid_x,
            "centroid_y": u.centroid_y,
            "centroid_z": u.centroid_z,
            "confidence": u.confidence.value,
            "generation_method": u.generation_method,
            "vuid_algorithm_version": u.vuid_algorithm_version,
            "vuid_full_hash": u.vuid_full_hash,
            "source_ids": u.source_ids,
            "status": u.status.value,
            "footprint_geom": {"type": "Polygon", "coordinates": geom_dict["coordinates"]},
            "polyhedron_wkt": u.polyhedron_wkt,
            "active_revision_id": str(active_rev.id) if active_rev else None,
            "revision_number": active_rev.revision_number if active_rev else 1,
            "created_at": u.created_at.isoformat()
        })
    return responses


@router.get("/{ulpin}/evidence")
def get_parcel_evidence(ulpin: str, db: Session = Depends(get_db)):
    from backend.services.evidence_service import EvidenceService
    from backend.schemas.evidence_contracts import EvidenceResponse
    
    service = EvidenceService(db)
    items = service.list_evidence_for_parcel(ulpin)
    return [
        EvidenceResponse(
            id=ev.id,
            parent_ulpin=ev.parent_ulpin,
            evidence_type=ev.evidence_type.value,
            provider=ev.provider,
            source_reference=ev.source_reference,
            checksum=ev.checksum,
            crs=ev.crs,
            acquisition_time=ev.acquisition_time,
            processing_version=ev.processing_version,
            metadata=ev.metadata,
            created_at=ev.created_at
        )
        for ev in items
    ]
