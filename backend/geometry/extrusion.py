from typing import NamedTuple
from shapely.geometry import Polygon


class VolumetricMetrics(NamedTuple):
    footprint_area_sqm: float
    height_m: float
    volume_cbm: float
    centroid_x: float
    centroid_y: float
    centroid_z: float
    polyhedron_wkt: str


def generate_polyhedral_surface_wkt(polygon: Polygon, z_min: float, z_max: float) -> str:
    """
    Constructs an OGC PolyhedralSurface WKT representation of the extruded prism:
    - Bottom face at z_min (CW winding when viewed from outside, or CCW from bottom)
    - Top face at z_max (CCW winding when viewed from above)
    - Side rectangular facets connecting bottom and top ring vertices.
    """
    ext_coords = list(polygon.exterior.coords)
    if ext_coords[0] == ext_coords[-1]:
        ring = ext_coords[:-1]
    else:
        ring = ext_coords
        
    n = len(ring)
    facets = []
    
    # 1. Bottom face: (x, y, z_min) - reversed so outward normal points down
    bottom_pts = [f"{x} {y} {z_min}" for (x, y) in reversed(ring)]
    bottom_pts.append(bottom_pts[0])
    facets.append(f"(({', '.join(bottom_pts)}))")
    
    # 2. Top face: (x, y, z_max) - CCW so outward normal points up
    top_pts = [f"{x} {y} {z_max}" for (x, y) in ring]
    top_pts.append(top_pts[0])
    facets.append(f"(({', '.join(top_pts)}))")
    
    # 3. Side faces: quad for each edge [i -> i+1]
    for i in range(n):
        j = (i + 1) % n
        p1 = ring[i]
        p2 = ring[j]
        # Quad vertices: (p1, z_min) -> (p2, z_min) -> (p2, z_max) -> (p1, z_max) -> (p1, z_min)
        quad = [
            f"{p1[0]} {p1[1]} {z_min}",
            f"{p2[0]} {p2[1]} {z_min}",
            f"{p2[0]} {p2[1]} {z_max}",
            f"{p1[0]} {p1[1]} {z_max}",
            f"{p1[0]} {p1[1]} {z_min}",
        ]
        facets.append(f"(({', '.join(quad)}))")
        
    return f"POLYHEDRALSURFACE Z ({', '.join(facets)})"


def compute_volumetric_extrusion(polygon: Polygon, z_min: float, z_max: float) -> VolumetricMetrics:
    """
    Computes volumetric metrics for a 2D polygon extruded over interval [z_min, z_max].
    """
    if z_min >= z_max:
        raise ValueError(f"z_min ({z_min}) must be strictly less than z_max ({z_max})")
    if polygon is None or polygon.is_empty:
        raise ValueError("Polygon cannot be empty.")
        
    area = round(float(polygon.area), 3)
    height = round(float(z_max - z_min), 3)
    volume = round(area * height, 3)
    
    centroid_2d = polygon.centroid
    centroid_x = round(float(centroid_2d.x), 3)
    centroid_y = round(float(centroid_2d.y), 3)
    centroid_z = round(float((z_min + z_max) / 2.0), 3)
    
    poly_wkt = generate_polyhedral_surface_wkt(polygon, z_min, z_max)
    
    return VolumetricMetrics(
        footprint_area_sqm=area,
        height_m=height,
        volume_cbm=volume,
        centroid_x=centroid_x,
        centroid_y=centroid_y,
        centroid_z=centroid_z,
        polyhedron_wkt=poly_wkt
    )
