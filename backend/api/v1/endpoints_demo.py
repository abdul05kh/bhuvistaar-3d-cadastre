import json
from pathlib import Path
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.db.session import get_db
from backend.services.parcel_service import ParcelService
from backend.services.evidence_service import EvidenceService
from backend.services.generation_service import GenerationService
from backend.services.validation_service import ValidationService
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.schemas.unit_contracts import UnitGenerateRequest


router = APIRouter(prefix="/demo", tags=["Demo Controller"])


@router.post("/reset")
def reset_demo(scenario: str = "defect", db: Session = Depends(get_db)):
    """Reset database to synthetic demo state and execute Gate A & B validation.
    
    scenario: 'defect' (default, sets up VRT-003 0.50m overlap for golden path) or 'clean'.
    """
    # 1. Clean previous state
    db.execute(text("DELETE FROM evaluation_runs;"))
    db.execute(text("DELETE FROM reproducibility_snapshots;"))
    db.execute(text("DELETE FROM validation_disagreements;"))
    db.execute(text("DELETE FROM ai_anomalies;"))
    db.execute(text("DELETE FROM ai_candidates;"))
    db.execute(text("DELETE FROM ai_observations;"))
    db.execute(text("DELETE FROM export_records;"))
    db.execute(text("DELETE FROM audit_events;"))
    db.execute(text("DELETE FROM approval_decisions;"))
    db.execute(text("DELETE FROM review_decisions;"))
    db.execute(text("DELETE FROM validation_issues;"))
    db.execute(text("DELETE FROM validation_runs;"))
    db.execute(text("DELETE FROM provenance_records;"))
    db.execute(text("DELETE FROM spatial_unit_revisions;"))
    db.execute(text("DELETE FROM spatial_units;"))
    db.execute(text("DELETE FROM evidence_sources;"))
    db.execute(text("DELETE FROM parent_parcels;"))
    db.commit()

    fixture_name = "synthetic_parcel_defect.json" if scenario == "defect" else "synthetic_parcel_clean.json"
    fixture_path = Path("fixtures") / fixture_name
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixture_data = json.load(f)

    # 2. Ingest Parcel
    p_service = ParcelService(db)
    parcel = p_service.ingest_parcel(ParcelIngestRequest(**fixture_data["parent_parcel"]))

    # 3. Register Evidence
    e_service = EvidenceService(db)
    evidence_registered = []
    for ev in fixture_data["evidence"]:
        saved_ev = e_service.register_evidence(EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev))
        evidence_registered.append(saved_ev.id)

    # 4. Generate 3D Units
    g_service = GenerationService(db)
    units = g_service.generate_3d_units(parcel.ulpin, UnitGenerateRequest(**fixture_data["building"]))

    # 5. Run Validation
    v_service = ValidationService(db)
    val_summary = v_service.run_validation(parcel.ulpin)

    return {
        "status": "RESET_SUCCESSFUL",
        "scenario": scenario,
        "parent_ulpin": parcel.ulpin,
        "parcel_area_sqm": parcel.area_sqm,
        "storage_srid": parcel.storage_srid,
        "units_count": len(units),
        "evidence_count": len(evidence_registered),
        "validation": {
            "run_id": val_summary.run_id,
            "rules_evaluated": val_summary.rules_evaluated,
            "passed_rules": val_summary.passed_rules,
            "failed_rules": val_summary.failed_rules,
            "blocker_count": val_summary.blocker_count,
            "can_approve": val_summary.can_approve
        }
    }
