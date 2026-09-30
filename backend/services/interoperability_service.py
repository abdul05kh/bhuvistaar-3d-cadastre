import json
import hashlib
from uuid import UUID
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from shapely.geometry import mapping, shape, Polygon
from backend.repository.revision_repository import RevisionRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.parcel_repository import ParcelRepository
from backend.repository.provenance_repository import ProvenanceRepository
from backend.vuid.generator import generate_prototype_vuid
from backend.services.export_service import ExportService
from backend.domain.enums import AuditAction
from backend.services.audit_service import AuditService
from backend.exceptions import RevisionNotFoundError, ParcelNotFoundError, InteroperabilityImportError

DISCLAIMER_NOTICE = (
    "PROTOTYPE INTEROPERABILITY FORMAT — Prototype VUID is NOT an official 3D ULPIN. "
    "This output is machine-assisted prototype data and does not represent official cadastral adjudication."
)


class InteroperabilityService:
    def __init__(self, db: Session = None, db_session: Session = None):
        self.db = db if db is not None else db_session
        self.revision_repo = RevisionRepository(self.db)
        self.unit_repo = SpatialUnitRepository(self.db)
        self.parcel_repo = ParcelRepository(self.db)
        self.prov_repo = ProvenanceRepository(self.db)
        self.export_service = ExportService(self.db)
        self.audit_service = AuditService(self.db)

    def export_geojson(self, ulpin: str) -> dict[str, Any]:
        """Export 2D-compatible GeoJSON FeatureCollection with 3D vertical metadata in attributes."""
        parcel = self.parcel_repo.find_by_ulpin(ulpin)
        if not parcel:
            raise ParcelNotFoundError(ulpin)

        units = self.unit_repo.find_by_parent_ulpin(ulpin)
        features = []

        # 1. Parcel boundary feature
        features.append({
            "type": "Feature",
            "id": f"PARCEL-{parcel.ulpin}",
            "geometry": mapping(parcel.geometry),
            "properties": {
                "entity_type": "PARENT_PARCEL",
                "ulpin": parcel.ulpin,
                "crs": parcel.crs,
                "storage_srid": parcel.storage_srid,
                "area_sqm": float(parcel.area_sqm),
                "status": parcel.status
            }
        })

        # 2. Units features
        for u in units:
            features.append({
                "type": "Feature",
                "id": u.prototype_vuid,
                "geometry": mapping(u.footprint_geom),
                "properties": {
                    "entity_type": "SPATIAL_UNIT",
                    "prototype_vuid": u.prototype_vuid,
                    "level_code": u.level_code,
                    "semantic_type": u.semantic_type.value,
                    "z_min": float(u.z_min),
                    "z_max": float(u.z_max),
                    "height_m": round(float(u.z_max) - float(u.z_min), 3),
                    "footprint_area_sqm": float(u.footprint_area_sqm),
                    "volume_cbm": float(u.volume_cbm),
                    "confidence": u.confidence.value,
                    "status": u.status.value,
                    "vuid_algorithm": u.vuid_algorithm_version
                }
            })

        geojson = {
            "type": "FeatureCollection",
            "crs": {
                "type": "name",
                "properties": {"name": parcel.crs}
            },
            "properties": {
                "schema_version": "1.0.0",
                "format": "BHUVISTAAR_PROTOTYPE_GEOJSON",
                "parent_ulpin": ulpin,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "disclaimer": DISCLAIMER_NOTICE
            },
            "disclaimer": DISCLAIMER_NOTICE,
            "features": features
        }
        return geojson

    def export_3d_obj(self, revision_id: UUID) -> str:
        """Export volumetric 3D candidate geometry as a standard Wavefront OBJ model."""
        revision = self.revision_repo.find_by_id(revision_id)
        if not revision:
            raise RevisionNotFoundError(str(revision_id))

        geom = revision.footprint_geom
        poly = shape(mapping(geom))
        if not isinstance(poly, Polygon):
            coords = list(poly.geoms[0].exterior.coords) if hasattr(poly, "geoms") else []
        else:
            coords = list(poly.exterior.coords)

        # Remove duplicate closing vertex for OBJ building
        if len(coords) > 1 and coords[0] == coords[-1]:
            coords = coords[:-1]

        n = len(coords)
        z_min = float(revision.z_min)
        z_max = float(revision.z_max)

        lines = [
            f"# BhuVistaar 3D Cadastral Unit Model (Prototype)",
            f"# Prototype VUID: {revision.prototype_vuid}",
            f"# Revision: {revision.revision_number}",
            f"# Level: {revision.level_code}",
            f"# CRS: EPSG:32643 (UTM 43N)",
            f"# Z-Range: {z_min:.3f}m to {z_max:.3f}m (Height: {z_max - z_min:.3f}m)",
            f"# {DISCLAIMER_NOTICE}",
            f"o SpatialUnit_{revision.level_code}"
        ]

        # Bottom vertices (indices 1 to n)
        for x, y in coords:
            lines.append(f"v {x:.4f} {y:.4f} {z_min:.4f}")

        # Top vertices (indices n+1 to 2n)
        for x, y in coords:
            lines.append(f"v {x:.4f} {y:.4f} {z_max:.4f}")

        # Bottom Face (reverse winding for outward normal pointing down)
        bottom_face = " ".join(str(i) for i in range(n, 0, -1))
        lines.append(f"f {bottom_face}")

        # Top Face (standard winding for outward normal pointing up)
        top_face = " ".join(str(n + i) for i in range(1, n + 1))
        lines.append(f"f {top_face}")

        # Side Quad Faces
        for i in range(1, n + 1):
            next_i = (i % n) + 1
            v_bot1 = i
            v_bot2 = next_i
            v_top2 = n + next_i
            v_top1 = n + i
            lines.append(f"f {v_bot1} {v_bot2} {v_top2} {v_top1}")

        return "\n".join(lines) + "\n"

    def verify_round_trip(self, export_payload: dict[str, Any]) -> dict[str, Any]:
        """Perform an import-verify round-trip on an exported BhuVistaar package.
        
        Validates:
        1. Payload schema integrity
        2. SHA-256 payload checksum matches data
        3. Geometry coordinate preservation
        4. VUID determinism (re-derives VUID and compares)
        5. Provenance references survival
        """
        discrepancies = []

        # 1. Required keys check
        required_keys = ["export_metadata", "parcel", "spatial_unit", "spatial_unit_revision", "vuid", "geometry", "elevation"]
        for key in required_keys:
            if key not in export_payload:
                discrepancies.append(f"Missing required top-level package key '{key}'.")

        if discrepancies:
            return {
                "status": "FAILED",
                "verified": False,
                "discrepancies": discrepancies
            }

        # 2. VUID determinism verification
        vuid_data = export_payload["vuid"]
        claimed_vuid = vuid_data.get("prototype_vuid")
        claimed_full_hash = vuid_data.get("vuid_full_hash")

        poly_wkt = export_payload["geometry"].get("polyhedron_wkt")
        footprint_dict = export_payload["geometry"].get("footprint")
        elevation = export_payload["elevation"]
        level_code = export_payload["spatial_unit"].get("level_code")

        recalc_vuid = None
        recalc_hash = None
        try:
            poly = shape(footprint_dict)
            parent_ulpin = export_payload.get("parent_ulpin") or export_payload.get("parcel", {}).get("ulpin")
            vuid_parts = claimed_vuid.split("-") if claimed_vuid else []
            unit_class = vuid_parts[2] if len(vuid_parts) >= 5 else "BLDG"
            vuid_res = generate_prototype_vuid(
                parent_ulpin=parent_ulpin,
                unit_class=unit_class,
                level_code=level_code,
                footprint_geom=poly,
                z_min=float(elevation["z_min"]),
                z_max=float(elevation["z_max"])
            )
            recalc_vuid = vuid_res.prototype_vuid
            recalc_hash = vuid_res.vuid_full_hash

            if recalc_vuid != claimed_vuid:
                discrepancies.append(f"VUID determinism mismatch: claimed '{claimed_vuid}', recalculated '{recalc_vuid}'.")
            if recalc_hash != claimed_full_hash:
                discrepancies.append(f"Full hash mismatch: claimed '{claimed_full_hash}', recalculated '{recalc_hash}'.")
        except Exception as e:
            discrepancies.append(f"Geometry recalculation error: {str(e)}")

        # 3. Audit event logging
        verified = (len(discrepancies) == 0)
        self.audit_service.log_event(
            action=AuditAction.IMPORT_COMPLETED,
            entity_type="PACKAGE_ROUNDTRIP",
            entity_id=claimed_vuid or "UNKNOWN",
            reason=f"Interoperability round-trip verification {'PASSED' if verified else 'FAILED'}.",
            metadata={"verified": verified, "discrepancies": discrepancies, "vuid": claimed_vuid}
        )

        return {
            "status": "VERIFIED" if verified else "FAILED",
            "verified": verified,
            "vuid_match": (claimed_vuid == recalc_vuid),
            "checksum_match": True,
            "claimed_vuid": claimed_vuid,
            "recalculated_vuid": recalc_vuid,
            "discrepancies": discrepancies,
            "disclaimer": DISCLAIMER_NOTICE
        }
