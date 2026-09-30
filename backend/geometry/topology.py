import math
from typing import Optional
from shapely.geometry import Polygon
from shapely.validation import explain_validity
from backend.config import settings


def check_finite_coordinates(polygon: Polygon) -> tuple[bool, Optional[str]]:
    """
    Checks that all coordinates in exterior and interior rings are finite floats.
    """
    if polygon is None or polygon.is_empty:
        return False, "Geometry is empty."
        
    for x, y in polygon.exterior.coords:
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            return False, f"Non-finite coordinate encountered: ({x}, {y})"
            
    for hole in polygon.interiors:
        for x, y in hole.coords:
            if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
                return False, f"Non-finite coordinate encountered in interior ring: ({x}, {y})"
                
    return True, None


def check_polygon_validity(polygon: Polygon) -> tuple[bool, Optional[str]]:
    """
    Verifies that the polygon is structurally and topologically valid according to OGC standards.
    """
    if polygon is None or polygon.is_empty:
        return False, "Geometry is empty."
    if not polygon.is_valid:
        reason = explain_validity(polygon)
        return False, reason
    return True, None


def verify_parent_containment(
    child: Polygon,
    parent: Polygon,
    tolerance: float = settings.PLANAR_CONTAINMENT_TOLERANCE_M
) -> tuple[bool, float, Optional[Polygon]]:
    """
    Verifies that child polygon footprint is completely within parent parcel.
    Does NOT clip or alter candidate geometry.
    Returns:
      (is_contained: bool, exterior_area_sqm: float, exterior_difference_geom: Optional[Polygon])
    """
    if child is None or parent is None:
        raise ValueError("Child and parent polygons must not be None.")
        
    # Difference: area of child that is NOT inside parent
    diff = child.difference(parent)
    
    if diff.is_empty:
        return True, 0.0, None
        
    diff_area = float(diff.area)
    if diff_area <= tolerance:
        return True, 0.0, None
        
    return False, round(diff_area, 3), diff
