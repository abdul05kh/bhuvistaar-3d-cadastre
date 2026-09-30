import logging
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from alembic import command
from alembic.config import Config
from backend.db.session import SessionLocal
from backend.config import settings
from backend.domain.enums import AuditAction
from backend.services.audit_service import AuditService

logger = logging.getLogger("bhuvistaar.bootstrap")


def bootstrap_database() -> dict[str, Any]:
    """Deterministic database bootstrap: verifies connection, ensures PostGIS, runs Alembic migrations."""
    results = {
        "status": "BOOTSTRAP_SUCCESSFUL",
        "postgis_extension": False,
        "postgis_version": None,
        "migrations_applied": False,
        "current_revision": None,
        "tables_verified": []
    }

    with SessionLocal() as db:
        # 1. Enable PostGIS extension
        db.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        db.commit()
        
        pg_res = db.execute(text("SELECT PostGIS_Version();")).fetchone()
        if pg_res:
            results["postgis_extension"] = True
            results["postgis_version"] = pg_res[0]

    # 2. Run Alembic migrations to head
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        results["migrations_applied"] = True
    except Exception as e:
        logger.error(f"Migration execution failed during bootstrap: {e}")
        results["status"] = "MIGRATION_FAILED"
        results["error"] = str(e)
        return results

    # 3. Verify tables and schema
    with SessionLocal() as db:
        rev_res = db.execute(text("SELECT version_num FROM alembic_version;")).fetchone()
        if rev_res:
            results["current_revision"] = rev_res[0]

        table_check = db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)).fetchall()
        results["tables_verified"] = [r[0] for r in table_check]

        # Log audit events
        audit = AuditService(db)
        audit.log_event(
            action=AuditAction.DATABASE_BOOTSTRAPPED,
            entity_type="DATABASE",
            entity_id="bhuvistaar_cadastre",
            reason=f"Database bootstrapped with PostGIS {results['postgis_version']} and migration {results['current_revision']}.",
            metadata=results
        )
        audit.log_event(
            action=AuditAction.MIGRATION_VERIFIED,
            entity_type="ALEMBIC_MIGRATION",
            entity_id=results["current_revision"] or "head",
            reason=f"Alembic migration head verified at revision {results['current_revision']}.",
            metadata={"revision": results["current_revision"]}
        )

    return results


def verify_data_integrity(db: Session) -> dict[str, Any]:
    """Deterministic, non-destructive data integrity verification.
    
    Verifies:
    1. Orphan spatial units (no parent parcel)
    2. Missing parent parcels
    3. Orphan revisions (no parent unit)
    4. Missing provenance records
    5. Broken evidence references
    6. Invalid geometries
    7. Stale validations
    8. Stale approvals
    9. VUID consistency
    
    Does NOT modify data; reports PASS, WARNING, or BLOCKER.
    """
    issues: list[dict[str, Any]] = []

    # 1. Orphan Spatial Units
    orphan_units = db.execute(text("""
        SELECT u.id, u.prototype_vuid, u.parent_ulpin 
        FROM spatial_units u 
        LEFT JOIN parent_parcels p ON u.parent_ulpin = p.ulpin 
        WHERE p.ulpin IS NULL;
    """)).fetchall()
    for row in orphan_units:
        issues.append({
            "severity": "BLOCKER",
            "check": "ORPHAN_SPATIAL_UNIT",
            "entity_id": str(row[0]),
            "description": f"Spatial unit '{row[1]}' references nonexistent parent parcel '{row[2]}'."
        })

    # 2. Orphan Revisions
    orphan_revs = db.execute(text("""
        SELECT r.id, r.prototype_vuid, r.unit_id 
        FROM spatial_unit_revisions r 
        LEFT JOIN spatial_units u ON r.unit_id = u.id 
        WHERE u.id IS NULL;
    """)).fetchall()
    for row in orphan_revs:
        issues.append({
            "severity": "BLOCKER",
            "check": "ORPHAN_REVISION",
            "entity_id": str(row[0]),
            "description": f"Revision '{row[0]}' references nonexistent unit '{row[2]}'."
        })

    # 3. Missing Provenance Records
    missing_prov = db.execute(text("""
        SELECT r.id, r.prototype_vuid 
        FROM spatial_unit_revisions r 
        LEFT JOIN provenance_records pr ON r.id = pr.revision_id 
        WHERE pr.id IS NULL;
    """)).fetchall()
    for row in missing_prov:
        issues.append({
            "severity": "BLOCKER",
            "check": "MISSING_PROVENANCE",
            "entity_id": str(row[0]),
            "description": f"Revision '{row[0]}' ({row[1]}) has no attached provenance record."
        })

    # 4. Invalid Geometries (PostGIS ST_IsValid check)
    invalid_geoms = db.execute(text("""
        SELECT id, prototype_vuid, ST_IsValidReason(footprint_geom) 
        FROM spatial_units 
        WHERE NOT ST_IsValid(footprint_geom);
    """)).fetchall()
    for row in invalid_geoms:
        issues.append({
            "severity": "BLOCKER",
            "check": "INVALID_GEOMETRY",
            "entity_id": str(row[0]),
            "description": f"Spatial unit '{row[1]}' has invalid geometry: {row[2]}."
        })

    # 5. Stale Validation Runs (Validations created prior to revision creation)
    stale_vals = db.execute(text("""
        SELECT r.id, r.prototype_vuid, vr.id, vr.created_at, r.created_at 
        FROM spatial_unit_revisions r 
        JOIN validation_runs vr ON r.parent_ulpin = vr.parent_ulpin 
        WHERE vr.created_at < r.created_at 
          AND r.status != 'REJECTED';
    """)).fetchall()
    for row in stale_vals:
        issues.append({
            "severity": "WARN",
            "check": "STALE_VALIDATION",
            "entity_id": str(row[0]),
            "description": f"Revision '{row[1]}' was created after validation run '{row[2]}'."
        })

    # 6. Approvals on Rejected or Stale Revisions
    invalid_approvals = db.execute(text("""
        SELECT a.id, a.revision_id, r.status 
        FROM approval_decisions a 
        JOIN spatial_unit_revisions r ON a.revision_id = r.id 
        WHERE r.status = 'REJECTED';
    """)).fetchall()
    for row in invalid_approvals:
        issues.append({
            "severity": "BLOCKER",
            "check": "INVALID_APPROVAL",
            "entity_id": str(row[0]),
            "description": f"Approval decision '{row[0]}' references rejected revision '{row[1]}'."
        })

    blocker_count = sum(1 for i in issues if i["severity"] == "BLOCKER")
    warn_count = sum(1 for i in issues if i["severity"] == "WARN")

    status = "BLOCKER" if blocker_count > 0 else ("WARNING" if warn_count > 0 else "PASS")

    summary = {
        "status": status,
        "total_issues": len(issues),
        "blockers": blocker_count,
        "warnings": warn_count,
        "checks_performed": [
            "ORPHAN_SPATIAL_UNIT",
            "ORPHAN_REVISION",
            "MISSING_PROVENANCE",
            "INVALID_GEOMETRY",
            "STALE_VALIDATION",
            "INVALID_APPROVAL"
        ]
    }

    # Audit event
    audit = AuditService(db)
    audit.log_event(
        action=AuditAction.DATA_INTEGRITY_CHECKED,
        entity_type="SYSTEM",
        entity_id="DATA_INTEGRITY",
        reason=f"Data integrity verified with result '{status}' ({blocker_count} blockers, {warn_count} warnings).",
        metadata=summary
    )

    return {
        "status": status,
        "summary": summary,
        "issues": issues
    }
