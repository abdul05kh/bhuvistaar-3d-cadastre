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


from backend.services.field_simulation_service import FieldSimulationService

router = APIRouter(prefix="/demo", tags=["Demo Controller"])


@router.get("/scenarios")

def list_scenarios(db: Session = Depends(get_db)):
    """List all available field simulation and judge demo scenarios."""
    service = FieldSimulationService(db)
    return service.get_catalog()


@router.post("/scenarios/{scenario_id}/execute")
def execute_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Execute a controlled field simulation scenario."""
    service = FieldSimulationService(db)
    return service.execute_scenario(scenario_id)


@router.post("/reset")
def reset_demo(scenario: str = "defect", db: Session = Depends(get_db)):
    """Reset database to synthetic demo state and execute Gate A & B validation.
    
    scenario: 'defect' (default, sets up VRT-003 0.50m overlap for golden path) or 'clean'.
    """
    service = FieldSimulationService(db)
    scenario_id = "clean" if scenario == "clean" else "defect"
    report = service.execute_scenario(scenario_id)

    # Fetch validation summary for backward compatibility
    v_service = ValidationService(db)
    val_summary = v_service.run_validation(report["parent_ulpin"])

    return {
        "status": "RESET_SUCCESSFUL",
        "scenario": scenario,
        "parent_ulpin": report["parent_ulpin"],
        "units_count": report["units_count"],
        "validation": {
            "run_id": val_summary.run_id,
            "rules_evaluated": val_summary.rules_evaluated,
            "passed_rules": val_summary.passed_rules,
            "failed_rules": val_summary.failed_rules,
            "blocker_count": val_summary.blocker_count,
            "can_approve": val_summary.can_approve
        }
    }

