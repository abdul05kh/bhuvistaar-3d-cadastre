from typing import Sequence
import shapely
from shapely.geometry import Polygon, LinearRing
from backend.config import settings


def _signed_area(coords: Sequence[tuple[float, float]]) -> float:
    """Calculates signed area using the Shoelace formula."""
    area = 0.0
    n = len(coords)
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]
    return area / 2.0


def normalize_linear_ring(
    coords: Sequence[tuple[float, float]],
    ensure_ccw: bool = True,
    precision: int = settings.COORDINATE_PRECISION_DECIMALS
) -> list[tuple[float, float]]:
    """
    Normalizes a coordinate sequence for a linear ring:
    1. Rounds each coordinate to `precision` decimal places.
    2. Drops consecutive identical vertices and duplicate closing vertex.
    3. Enforces ring winding (CCW for exterior, CW for holes).
    4. Cyclically shifts vertices so the lexicographically minimum vertex is first.
    5. Re-closes the ring (first == last).
    """
    # Round coordinates
    pts = [(round(float(c[0]), precision), round(float(c[1]), precision)) for c in coords]
    
    # Strip closing duplicate if present
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
        
    # Remove consecutive duplicate vertices
    cleaned: list[tuple[float, float]] = []
    for pt in pts:
        if not cleaned or pt != cleaned[-1]:
            cleaned.append(pt)
    if len(cleaned) > 1 and cleaned[0] == cleaned[-1]:
        cleaned.pop()
        
    if len(cleaned) < 3:
        raise ValueError(f"Linear ring must contain at least 3 distinct vertices; found {len(cleaned)}.")
        
    # Check winding
    area = _signed_area(cleaned)
    is_current_ccw = area > 0
    if ensure_ccw and not is_current_ccw:
        cleaned.reverse()
    elif not ensure_ccw and is_current_ccw:
        cleaned.reverse()
        
    # Find lexicographically smallest vertex (min X, then min Y)
    min_idx = 0
    min_pt = cleaned[0]
    for idx, pt in enumerate(cleaned[1:], start=1):
        if pt < min_pt:
            min_pt = pt
            min_idx = idx
            
    # Cyclically shift vertices so min_pt is at index 0
    canonical_pts = cleaned[min_idx:] + cleaned[:min_idx]
    
    # Re-close ring
    canonical_pts.append(canonical_pts[0])
    return canonical_pts


def canonicalize_polygon(
    polygon: Polygon,
    precision: int = settings.COORDINATE_PRECISION_DECIMALS
) -> Polygon:
    """
    Produces a mathematically canonical Polygon representation:
    - Exterior ring normalized to CCW starting at lexicographically smallest vertex.
    - Each hole normalized to CW starting at lexicographically smallest vertex.
    - Multiple holes sorted deterministically by (centroid.x, centroid.y, area).
    """
    if polygon is None or polygon.is_empty:
        raise ValueError("Cannot canonicalize an empty polygon.")
        
    # Canonicalize exterior ring
    ext_coords = normalize_linear_ring(polygon.exterior.coords, ensure_ccw=True, precision=precision)
    
    # Canonicalize and sort interior rings (holes)
    canonical_holes = []
    for hole in polygon.interiors:
        hole_coords = normalize_linear_ring(hole.coords, ensure_ccw=False, precision=precision)
        hole_ring = LinearRing(hole_coords)
        canonical_holes.append((
            round(hole_ring.centroid.x, precision),
            round(hole_ring.centroid.y, precision),
            round(hole_ring.area, precision),
            hole_coords
        ))
        
    # Sort holes deterministically by (centroid_x, centroid_y, area)
    canonical_holes.sort(key=lambda item: (item[0], item[1], item[2]))
    sorted_hole_coords = [item[3] for item in canonical_holes]
    
    return Polygon(ext_coords, sorted_hole_coords)


def canonical_wkb_hex(polygon: Polygon, precision: int = settings.COORDINATE_PRECISION_DECIMALS) -> str:
    """
    Returns the deterministic Well-Known Binary hex string of the canonicalized polygon.
    """
    canon_poly = canonicalize_polygon(polygon, precision=precision)
    # Output WKB with standard big-endian or little-endian, using hex format
    return shapely.to_wkb(canon_poly, hex=True, byte_order=1)
