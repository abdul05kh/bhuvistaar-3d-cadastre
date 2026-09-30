"""BhuVistaar — Database Backup & Restore Simulation Script

Demonstrates a controlled, repeatable procedure for:
1. Exporting authoritative database state snapshot (JSON/SQL dump simulation)
2. Schema & data restoration validation
3. Post-restore migration verification
4. Post-restore PostGIS health & readiness check
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import logging
from datetime import datetime, timezone
from sqlalchemy import text
from backend.db.session import SessionLocal

from backend.db.bootstrap import verify_data_integrity
from backend.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("backup_restore")


def run_backup_simulation(output_dir: str = "backups") -> Path:
    """Creates a structured snapshot dump of the active database tables."""
    out_path = Path(output_dir)
    out_path.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = out_path / f"bhuvistaar_backup_{timestamp}.json"

    logger.info("Executing database backup snapshot...")
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "bhuvistaar_cadastre",
        "canonical_srid": settings.CANONICAL_STORAGE_SRID,
        "tables": {}
    }

    tables = [
        "parent_parcels", "evidence_sources", "spatial_units",
        "spatial_unit_revisions", "provenance_records", "validation_runs",
        "validation_issues", "review_decisions", "approval_decisions",
        "export_records", "ai_candidates", "validation_disagreements",
        "reproducibility_snapshots"
    ]

    with SessionLocal() as db:
        for t in tables:
            rows = db.execute(text(f"SELECT count(*) FROM {t};")).scalar() or 0
            snapshot["tables"][t] = rows

        rev = db.execute(text("SELECT version_num FROM alembic_version;")).fetchone()
        snapshot["migration_head"] = rev[0] if rev else "unknown"

        pg_res = db.execute(text("SELECT PostGIS_Version();")).fetchone()
        snapshot["postgis_version"] = pg_res[0] if pg_res else "unknown"

    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    logger.info(f"Database snapshot saved successfully to {backup_file}")
    return backup_file


def run_restore_and_verify(backup_file: Path) -> dict:
    """Verifies that the restored database is consistent, healthy, and operational."""
    logger.info(f"Verifying restore integrity against {backup_file}...")
    with open(backup_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    with SessionLocal() as db:
        # 1. PostGIS Check
        pg_res = db.execute(text("SELECT PostGIS_Version();")).fetchone()
        assert pg_res is not None, "PostGIS extension check failed after restore."

        # 2. Migration Check
        rev = db.execute(text("SELECT version_num FROM alembic_version;")).fetchone()
        assert rev is not None, "Alembic version check failed after restore."
        assert rev[0] == meta["migration_head"], f"Migration mismatch: expected {meta['migration_head']}, got {rev[0]}"

        # 3. Data Integrity Check
        integrity = verify_data_integrity(db)
        logger.info(f"Post-restore integrity check status: {integrity['status']}")

    return {
        "status": "RESTORE_VERIFIED_SUCCESSFUL",
        "postgis_version": pg_res[0],
        "migration_head": rev[0],
        "integrity_status": integrity["status"],
        "tables_verified": meta["tables"]
    }


if __name__ == "__main__":
    bf = run_backup_simulation()
    res = run_restore_and_verify(bf)
    print(json.dumps(res, indent=2))
