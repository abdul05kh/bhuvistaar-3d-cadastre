from pyproj import CRS, Transformer
from shapely.geometry import Polygon, shape
from shapely.ops import transform
from backend.exceptions import InvalidCRSError
from backend.config import settings


def parse_and_validate_crs(crs_str: str) -> CRS:
    """
    Parses and validates an incoming CRS string.
    Ensures the CRS is recognized by PROJ.
    """
    if not crs_str or not isinstance(crs_str, str):
        raise InvalidCRSError("CRS string must be a non-empty string.")
    try:
        crs = CRS.from_user_input(crs_str.strip())
        return crs
    except Exception as e:
        raise InvalidCRSError(f"Unrecognized or invalid CRS '{crs_str}': {str(e)}")


def assert_projected_metric_crs(crs_str: str) -> CRS:
    """
    Ensures the CRS is a projected coordinate reference system with linear units in metres.
    Rejects geographic coordinate systems (e.g. EPSG:4326) where coordinates are in degrees.
    """
    crs = parse_and_validate_crs(crs_str)
    if not crs.is_projected:
        raise InvalidCRSError(
            f"CRS '{crs_str}' is geographic (angular degrees). "
            f"BhuVistaar requires an explicit projected CRS with linear units in metres (e.g. EPSG:32643)."
        )
    return crs


def transform_polygon_to_srid(polygon: Polygon, source_crs_str: str, target_srid: int = settings.CANONICAL_STORAGE_SRID) -> Polygon:
    """
    Transforms a Shapely Polygon from source CRS to target storage SRID.
    """
    src_crs = assert_projected_metric_crs(source_crs_str)
    tgt_crs = CRS.from_epsg(target_srid)
    
    if src_crs.to_epsg() == target_srid:
        return polygon
        
    transformer = Transformer.from_crs(src_crs, tgt_crs, always_xy=True)
    return transform(transformer.transform, polygon)
