import hashlib
from typing import NamedTuple
from shapely.geometry import Polygon
from backend.geometry.normalization import canonical_wkb_hex
from backend.config import settings


class VUIDResult(NamedTuple):
    prototype_vuid: str
    vuid_full_hash: str
    vuid_algorithm_version: str


def generate_prototype_vuid(
    parent_ulpin: str,
    unit_class: str,
    level_code: str,
    footprint_geom: Polygon,
    z_min: float,
    z_max: float,
    algorithm_version: str = "v1"
) -> VUIDResult:
    """
    Deterministically generates a Prototype Volumetric Unique Identifier (VUID).
    
    Representation Invariance:
    - Independent of vertex start index in polygon boundary rings.
    - Independent of exterior ring winding (normalized to CCW).
    - Independent of interior hole ordering (sorted deterministically).
    - Rounded to 3 decimal places (1mm).
    
    Format:
      BV-{parent_ulpin}-{unit_class}-{level_code}-{short_hash}
      
    DISCLAIMER:
      This is a prototype volumetric identifier and is NOT an official Government 3D ULPIN.
    """
    if not parent_ulpin or len(parent_ulpin) != 14 or not parent_ulpin.isdigit():
        raise ValueError(f"Invalid parent ULPIN '{parent_ulpin}': must be 14 numeric digits.")
    if z_min >= z_max:
        raise ValueError(f"z_min ({z_min}) must be strictly less than z_max ({z_max}).")
        
    canonical_wkb = canonical_wkb_hex(footprint_geom, precision=settings.COORDINATE_PRECISION_DECIMALS)
    z_str = f"{round(z_min, 3):.3f}:{round(z_max, 3):.3f}"
    
    canonical_buffer = f"{algorithm_version}|{parent_ulpin}|{unit_class.upper()}|{level_code.upper()}|{canonical_wkb}|{z_str}"
    
    full_hash = hashlib.sha256(canonical_buffer.encode("utf-8")).hexdigest().upper()
    short_hash = full_hash[:6]
    
    prototype_vuid = f"BV-{parent_ulpin}-{unit_class.upper()}-{level_code.upper()}-{short_hash}"
    
    return VUIDResult(
        prototype_vuid=prototype_vuid,
        vuid_full_hash=full_hash,
        vuid_algorithm_version=algorithm_version
    )
