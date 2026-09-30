from sqlalchemy.orm import Session
from shapely.geometry import shape, Polygon
from backend.domain.parcel import ParentParcel
from backend.domain.enums import UnitStatus
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.repository.parcel_repository import ParcelRepository
from backend.geometry.crs import assert_projected_metric_crs, transform_polygon_to_srid
from backend.geometry.topology import check_polygon_validity, check_finite_coordinates
from backend.exceptions import InvalidGeometryError
from backend.config import settings


class ParcelService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ParcelRepository(db)

    def ingest_parcel(self, request: ParcelIngestRequest) -> ParentParcel:
        # 1. Parse and validate CRS
        assert_projected_metric_crs(request.crs)

        # 2. Parse GeoJSON polygon to Shapely
        raw_geom = shape(request.geometry.model_dump())
        if not isinstance(raw_geom, Polygon):
            raise InvalidGeometryError("Parent parcel geometry must be a Polygon.")

        # 3. Check finite coordinates
        finite_ok, finite_err = check_finite_coordinates(raw_geom)
        if not finite_ok:
            raise InvalidGeometryError(f"Coordinate error: {finite_err}")

        # 4. Check polygon topology validity
        valid_ok, valid_err = check_polygon_validity(raw_geom)
        if not valid_ok:
            raise InvalidGeometryError(f"Polygon topology error: {valid_err}")

        # 5. Transform to canonical storage SRID (32643) if needed
        transformed_geom = transform_polygon_to_srid(
            polygon=raw_geom,
            source_crs_str=request.crs,
            target_srid=settings.CANONICAL_STORAGE_SRID
        )

        area_sqm = round(float(transformed_geom.area), 3)

        parcel = ParentParcel(
            ulpin=request.ulpin,
            crs=request.crs,
            storage_srid=settings.CANONICAL_STORAGE_SRID,
            geometry=transformed_geom,
            area_sqm=area_sqm,
            status=UnitStatus.DRAFT,
            metadata=request.metadata
        )

        return self.repo.save(parcel)

    def get_parcel(self, ulpin: str) -> ParentParcel:
        parcel = self.repo.find_by_ulpin(ulpin)
        if not parcel:
            from backend.exceptions import ParcelNotFoundError
            raise ParcelNotFoundError(ulpin)
        return parcel
