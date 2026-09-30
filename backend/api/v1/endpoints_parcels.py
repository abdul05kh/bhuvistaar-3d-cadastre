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
