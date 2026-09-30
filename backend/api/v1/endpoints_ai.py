"""AI Intelligence API Endpoints (Slice 3).

Exposes:
- AI Inference Pipeline execution
- Candidate inspection, acceptance, and rejection
- Anomaly listing and reviewer queue prioritization
- Fact-based explanation synthesis
- End-to-end Trace Origin lineage traversal
- Model registry and evaluation benchmarking
- AI demo scenarios
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.ai.services.ai_orchestrator import AIOrchestrator
from backend.ai.services.candidate_governance_service import CandidateGovernanceService
from backend.ai.models.explainer import CadastralExplainer
from backend.ai.registry.model_registry import get_registered_models, get_model_by_id
from backend.ai.evaluators.evaluator import AIEvaluationHarness
from backend.ai.schemas.candidate import (
    CandidateSpatialUnit,
    CandidateReviewRequest
)
from backend.ai.schemas.anomaly import AIAnomaly
from backend.ai.schemas.summary import (
    AIAssistanceSummary,
    ReviewerQueueResponse,
    FactBasedExplanationResponse
)
from backend.ai.schemas.lineage import TraceOriginResponse
from backend.ai.schemas.registry import ModelRegistryResponse, ModelCard
from backend.ai.schemas.disagreement import DisagreementListResponse
from backend.ai.schemas.reproducibility import ReproducibilitySnapshotResponse, ReproducibilityVerificationRequest
from backend.ai.schemas.model_comparison import ModelComparisonRequest, ModelComparisonResponse
from backend.ai.services.disagreement_engine import ValidationDisagreementEngine
from backend.ai.services.reproducibility_service import ReproducibilityService
from backend.ai.services.model_comparison_service import ModelComparisonService
from backend.db.models import (
    AICandidateModel,
    AIAnomalyModel,
    ValidationIssueModel,
    ValidationRunModel,
    EvaluationRunModel
)
from backend.exceptions import AICandidateNotFoundError

router = APIRouter(prefix="/ai", tags=["AI Intelligence (Slice 3 & 4)"])


@router.post("/infer/{parent_ulpin}")
def run_ai_inference(
    parent_ulpin: str,
    actor_id: str = Query(default="surveyor_officer_01", description="Triggering actor"),
    db: Session = Depends(get_db)
):
    """Executes the AI inference pipeline: Layer A (Evidence) -> Layer B (Candidates) -> Layer C (Anomalies) -> Layer D (Summary)."""
    orchestrator = AIOrchestrator(db)
    candidates, anomalies, summary = orchestrator.run_inference_pipeline(
        parent_ulpin=parent_ulpin,
        actor_id=actor_id
    )

    return {
        "status": "INFERENCE_COMPLETED",
        "parent_ulpin": parent_ulpin,
        "candidates": [c.model_dump() for c in candidates],
        "anomalies": [a.model_dump() for a in anomalies],
        "summary": summary.model_dump()
    }


@router.get("/candidates/{parent_ulpin}")
def list_candidates(
    parent_ulpin: str,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: AI_CANDIDATE, ACCEPTED, REJECTED"),
    confidence_band: Optional[str] = Query(None, description="Filter by band: HIGH, MEDIUM, LOW"),
    db: Session = Depends(get_db)
):
    """Lists AI proposed candidates for a parent parcel with optional status/confidence filters."""
    query = db.query(AICandidateModel).filter(AICandidateModel.parent_ulpin == parent_ulpin)
    if status_filter:
        query = query.filter(AICandidateModel.status == status_filter)
    if confidence_band:
        query = query.filter(AICandidateModel.confidence_band == confidence_band)

    candidates = query.order_by(AICandidateModel.z_min.asc()).all()

    return {
        "parent_ulpin": parent_ulpin,
        "count": len(candidates),
        "candidates": [
            {
                "candidate_id": c.candidate_id,
                "parent_ulpin": c.parent_ulpin,
                "level_code": c.level_code,
                "semantic_type": c.semantic_type,
                "z_min": float(c.z_min),
                "z_max": float(c.z_max),
                "confidence": float(c.confidence),
                "confidence_band": c.confidence_band,
                "status": c.status,
                "source_evidence_ids": c.source_evidence_ids or [],
                "reason_codes": c.reason_codes or [],
                "footprint_geojson": c.footprint_geojson,
                "footprint_area_sqm": float(c.footprint_area_sqm),
                "volume_cbm": float(c.volume_cbm),
                "centroid": [float(c.centroid_x), float(c.centroid_y), float(c.centroid_z)],
                "model": {"name": c.model_name, "version": c.model_version},
                "governed_unit_id": str(c.governed_unit_id) if c.governed_unit_id else None,
                "governed_revision_id": str(c.governed_revision_id) if c.governed_revision_id else None,
                "rejection_reason": c.rejection_reason,
                "reviewed_by": c.reviewed_by,
                "reviewed_at": c.reviewed_at.isoformat() if c.reviewed_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in candidates
        ]
    }


@router.get("/candidates/detail/{candidate_id}")
def get_candidate_detail(candidate_id: str, db: Session = Depends(get_db)):
    """Retrieves full detail of an AI candidate proposal."""
    cand = db.query(AICandidateModel).filter(AICandidateModel.candidate_id == candidate_id).first()
    if not cand:
        raise AICandidateNotFoundError(candidate_id)

    return {
        "candidate_id": cand.candidate_id,
        "parent_ulpin": cand.parent_ulpin,
        "level_code": cand.level_code,
        "semantic_type": cand.semantic_type,
        "vertical_extent": {"z_min": float(cand.z_min), "z_max": float(cand.z_max)},
        "confidence": float(cand.confidence),
        "confidence_band": cand.confidence_band,
        "status": cand.status,
        "source_evidence_ids": cand.source_evidence_ids or [],
        "reason_codes": cand.reason_codes or [],
        "footprint_geojson": cand.footprint_geojson,
        "footprint_area_sqm": float(cand.footprint_area_sqm),
        "volume_cbm": float(cand.volume_cbm),
        "centroid": [float(cand.centroid_x), float(cand.centroid_y), float(cand.centroid_z)],
        "model": {"name": cand.model_name, "version": cand.model_version},
        "governed_unit_id": str(cand.governed_unit_id) if cand.governed_unit_id else None,
        "governed_revision_id": str(cand.governed_revision_id) if cand.governed_revision_id else None,
        "rejection_reason": cand.rejection_reason,
        "reviewed_by": cand.reviewed_by,
        "reviewed_at": cand.reviewed_at.isoformat() if cand.reviewed_at else None,
        "created_at": cand.created_at.isoformat() if cand.created_at else None
    }


@router.post("/candidates/{candidate_id}/accept")
def accept_candidate(
    candidate_id: str,
    request: CandidateReviewRequest,
    db: Session = Depends(get_db)
):
    """Human officer accepts AI proposal into governed spatial unit revision with deterministic VUID and validation."""
    gov_service = CandidateGovernanceService(db)
    unit, rev, val_summary = gov_service.accept_candidate(
        candidate_id=candidate_id,
        reviewer_id=request.reviewer_id,
        justification=request.justification
    )

    return {
        "status": "ACCEPTED_INTO_GOVERNANCE",
        "candidate_id": candidate_id,
        "spatial_unit_id": str(unit.id),
        "prototype_vuid": unit.prototype_vuid,
        "revision_id": str(rev.id),
        "revision_number": rev.revision_number,
        "validation_gate_a": val_summary
    }


@router.post("/candidates/{candidate_id}/reject")
def reject_candidate(
    candidate_id: str,
    request: CandidateReviewRequest,
    db: Session = Depends(get_db)
):
    """Human officer rejects AI proposal with mandatory rationale; proposal is preserved in audit history."""
    gov_service = CandidateGovernanceService(db)
    cand = gov_service.reject_candidate(
        candidate_id=candidate_id,
        reviewer_id=request.reviewer_id,
        justification=request.justification
    )

    return {
        "status": "REJECTED",
        "candidate_id": cand.candidate_id,
        "rejection_reason": cand.rejection_reason,
        "reviewed_by": cand.reviewed_by,
        "reviewed_at": cand.reviewed_at.isoformat() if cand.reviewed_at else None
    }


@router.get("/anomalies/{parent_ulpin}")
def list_anomalies(
    parent_ulpin: str,
    unresolved_only: bool = Query(default=True, description="Filter only active unresolved anomalies"),
    db: Session = Depends(get_db)
):
    """Lists detected topological, evidential, and elevation anomalies for a parcel."""
    query = db.query(AIAnomalyModel).filter(AIAnomalyModel.parent_ulpin == parent_ulpin)
    if unresolved_only:
        query = query.filter(AIAnomalyModel.resolved == False)

    anomalies = query.order_by(AIAnomalyModel.created_at.desc()).all()

    return {
        "parent_ulpin": parent_ulpin,
        "count": len(anomalies),
        "anomalies": [
            {
                "anomaly_id": a.anomaly_id,
                "parent_ulpin": a.parent_ulpin,
                "anomaly_type": a.anomaly_type,
                "severity": a.severity,
                "affected_units": a.affected_units or [],
                "evidence_ids": a.evidence_ids or [],
                "confidence": float(a.confidence),
                "reason_codes": a.reason_codes or [],
                "recommended_action": a.recommended_action,
                "model": {"name": a.model_name, "version": a.model_version},
                "resolved": a.resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in anomalies
        ]
    }


@router.get("/summary/{parent_ulpin}", response_model=AIAssistanceSummary)
def get_ai_summary(parent_ulpin: str, db: Session = Depends(get_db)):
    """Provides high-level operational intelligence summary for reviewer dashboard."""
    orchestrator = AIOrchestrator(db)
    return orchestrator.get_summary(parent_ulpin)


@router.get("/queue/{parent_ulpin}", response_model=ReviewerQueueResponse)
def get_reviewer_queue(parent_ulpin: str, db: Session = Depends(get_db)):
    """Provides prioritized reviewer attention queue sorted by urgency (Blockers > Anomalies > Low Confidence > Unreviewed)."""
    orchestrator = AIOrchestrator(db)
    return orchestrator.get_reviewer_queue(parent_ulpin)


@router.get("/explain/{candidate_id}", response_model=FactBasedExplanationResponse)
def get_fact_based_explanation(candidate_id: str, db: Session = Depends(get_db)):
    """Generates human-readable explanation strictly grounded in deterministic facts, measurements, and evidence."""
    cand = db.query(AICandidateModel).filter(AICandidateModel.candidate_id == candidate_id).first()
    if not cand:
        raise AICandidateNotFoundError(candidate_id)

    anoms = db.query(AIAnomalyModel).filter(
        AIAnomalyModel.parent_ulpin == cand.parent_ulpin,
        AIAnomalyModel.resolved == False
    ).all()
    matching_anoms = [
        AIAnomaly(
            anomaly_id=a.anomaly_id,
            parent_ulpin=a.parent_ulpin,
            anomaly_type=a.anomaly_type,
            severity=a.severity,
            affected_units=a.affected_units or [],
            evidence_ids=a.evidence_ids or [],
            confidence=float(a.confidence),
            reason_codes=a.reason_codes or [],
            recommended_action=a.recommended_action,
            model={"name": a.model_name, "version": a.model_version},
            resolved=a.resolved
        )
        for a in anoms if cand.level_code in (a.affected_units or [])
    ]

    cand_schema = CandidateSpatialUnit(
        candidate_id=cand.candidate_id,
        parent_ulpin=cand.parent_ulpin,
        source_evidence_ids=cand.source_evidence_ids or [],
        geometry=cand.footprint_geojson,
        vertical_extent={"z_min": float(cand.z_min), "z_max": float(cand.z_max)},
        semantic_type=cand.semantic_type,
        level_code=cand.level_code,
        confidence=float(cand.confidence),
        confidence_band=cand.confidence_band,
        reason_codes=cand.reason_codes or [],
        model={"name": cand.model_name, "version": cand.model_version},
        status=cand.status,
        footprint_area_sqm=float(cand.footprint_area_sqm),
        volume_cbm=float(cand.volume_cbm),
        centroid_x=float(cand.centroid_x),
        centroid_y=float(cand.centroid_y),
        centroid_z=float(cand.centroid_z)
    )

    return CadastralExplainer.explain_candidate(
        candidate=cand_schema,
        associated_anomalies=matching_anoms
    )


@router.get("/trace-origin/{identifier}", response_model=TraceOriginResponse)
def trace_origin(identifier: str, db: Session = Depends(get_db)):
    """Traverses complete end-to-end data lineage from source evidence to approval and export."""
    gov_service = CandidateGovernanceService(db)
    return gov_service.trace_origin(identifier)


@router.get("/models", response_model=ModelRegistryResponse)
def list_models():
    """Lists registered prototype models and comprehensive model card specifications."""
    models = get_registered_models()
    return ModelRegistryResponse(registered_models=models, total_models=len(models))


@router.post("/evaluate")
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    """Executes empirical evaluation harness against 10 synthetic ground truth cadastral scenarios."""
    return AIEvaluationHarness.run_benchmark_evaluation(db=db)


@router.get("/disagreements/{parent_ulpin}", response_model=DisagreementListResponse)
def get_validation_disagreements(
    parent_ulpin: str,
    actor_id: str = Query(default="surveyor_officer_01", description="Triggering actor"),
    db: Session = Depends(get_db)
):
    """Analyzes and catalogs tensions/disagreements between AI proposal confidence, deterministic validation, and human review."""
    engine = ValidationDisagreementEngine(db)
    return engine.analyze_disagreements(parent_ulpin=parent_ulpin, actor_id=actor_id)


@router.get("/explain/validation/{run_id}")
def explain_validation_run(run_id: str, db: Session = Depends(get_db)):
    """Provides deep, transparent, human-readable explanations of every validation issue and blocker in a validation run."""
    val_run = db.query(ValidationRunModel).filter(ValidationRunModel.id == run_id).first()
    if not val_run:
        return {"run_id": run_id, "issues": [], "summary": "Validation run not found."}

    issues = db.query(ValidationIssueModel).filter(ValidationIssueModel.run_id == val_run.id).all()
    explanations = [
        CadastralExplainer.explain_validation_issue({
            "rule_code": iss.rule_code,
            "severity": iss.severity,
            "object_id": iss.object_id,
            "passed": iss.passed,
            "message": iss.message,
            "measured_value": iss.measured_value,
            "threshold": iss.threshold,
            "suggested_action": iss.suggested_action
        })
        for iss in issues
    ]

    return {
        "run_id": str(val_run.id),
        "parent_ulpin": val_run.parent_ulpin,
        "validator_version": val_run.validator_version,
        "ruleset_version": "1.0.0",
        "rules_evaluated": val_run.rules_evaluated,
        "blocker_count": val_run.blocker_count,
        "can_approve": val_run.can_approve,
        "explanations": explanations
    }


@router.get("/reproducibility/{target_id}", response_model=ReproducibilitySnapshotResponse)
def get_reproducibility_snapshot(
    target_id: str,
    actor_id: str = Query(default="audit_officer", description="Auditing actor"),
    db: Session = Depends(get_db)
):
    """Generates or retrieves cryptographic reproducibility snapshot for candidate proposal or governed spatial unit."""
    service = ReproducibilityService(db)
    return service.generate_snapshot(target_id=target_id, actor_id=actor_id)


@router.post("/reproducibility/verify")
def verify_reproducibility(
    request: ReproducibilityVerificationRequest,
    db: Session = Depends(get_db)
):
    """Recomputes cryptographic snapshot hash from underlying database state to verify reproducibility."""
    service = ReproducibilityService(db)
    return service.verify_reproducibility(target_id=request.target_id)


@router.post("/models/compare", response_model=ModelComparisonResponse)
def compare_models(
    request: ModelComparisonRequest,
    db: Session = Depends(get_db)
):
    """Compares two model configurations or baseline on proposal count, mean confidence, anomalies, and validation blockers."""
    service = ModelComparisonService(db)
    return service.compare_models(
        model_a_id=request.model_a_id,
        model_b_id=request.model_b_id,
        parent_ulpin=request.parent_ulpin
    )


@router.get("/evaluations/history")
def get_evaluation_history(db: Session = Depends(get_db)):
    """Retrieves historical empirical evaluation benchmark runs."""
    runs = db.query(EvaluationRunModel).order_by(EvaluationRunModel.created_at.desc()).limit(10).all()
    return {
        "count": len(runs),
        "runs": [
            {
                "run_id": r.run_id,
                "scenario_name": r.scenario_name,
                "dataset_name": r.dataset_name,
                "dataset_version": r.dataset_version,
                "is_synthetic": r.is_synthetic,
                "model_name": r.model_name,
                "model_version": r.model_version,
                "ruleset_version": r.ruleset_version,
                "total_cases": r.total_cases,
                "metrics": r.metrics_json,
                "disagreements_count": r.disagreements_count,
                "execution_time_ms": float(r.execution_time_ms),
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in runs
        ]
    }


@router.post("/scenarios/{scenario_key}")
def load_ai_demo_scenario(
    scenario_key: str,
    db: Session = Depends(get_db)
):
    """Loads a designated AI demo scenario for demonstration to judges:
    - flagship: golden path with L01/L02 0.5m overlap blocker
    - evidence-conflict: discordant evidence sources for Level 2
    - low-confidence: ambiguous hand-drawn terrace sketch with 0.45 confidence
    - vertical-gap: unexplained 1.5m inter-floor gap
    """
    from backend.api.v1.endpoints_demo import reset_demo
    # First reset DB with defect scenario
    reset_demo(scenario="defect", db=db)

    parent_ulpin = "12345678901234"
    orchestrator = AIOrchestrator(db)

    custom_levels = None
    if scenario_key == "evidence-conflict":
        custom_levels = [
            {"level_code": "Ground", "z_min": 100.0, "z_max": 103.0, "confidence": 0.95, "source_evidence_ids": ["EVID-002"]},
            {"level_code": "L01", "z_min": 103.0, "z_max": 106.0, "confidence": 0.94, "source_evidence_ids": ["EVID-003"]},
            {"level_code": "L02", "z_min": 106.0, "z_max": 109.0, "confidence": 0.70, "source_evidence_ids": ["EVID-003", "EVID-SURVEY-MISMATCH"]}
        ]
    elif scenario_key == "low-confidence":
        custom_levels = [
            {"level_code": "Ground", "z_min": 100.0, "z_max": 103.0, "confidence": 0.95, "source_evidence_ids": ["EVID-002"]},
            {"level_code": "L01", "z_min": 103.0, "z_max": 106.0, "confidence": 0.94, "source_evidence_ids": ["EVID-003"]},
            {"level_code": "L02", "z_min": 106.0, "z_max": 109.0, "confidence": 0.91, "source_evidence_ids": ["EVID-003"]},
            {"level_code": "RoofTerrace", "z_min": 109.0, "z_max": 112.0, "confidence": 0.45, "source_evidence_ids": ["EVID-SKETCH-PARTIAL"]}
        ]
    elif scenario_key == "vertical-gap":
        custom_levels = [
            {"level_code": "Ground", "z_min": 100.0, "z_max": 103.0, "confidence": 0.95, "source_evidence_ids": ["EVID-002"]},
            {"level_code": "L01", "z_min": 104.5, "z_max": 107.5, "confidence": 0.91, "source_evidence_ids": ["EVID-003"]}
        ]
    else:  # Flagship
        custom_levels = [
            {"level_code": "B1", "z_min": 97.0, "z_max": 100.0, "confidence": 0.88, "source_evidence_ids": ["EVID-003"]},
            {"level_code": "Ground", "z_min": 100.0, "z_max": 103.0, "confidence": 0.95, "source_evidence_ids": ["EVID-002", "EVID-003"]},
            {"level_code": "L01", "z_min": 103.0, "z_max": 106.5, "confidence": 0.94, "source_evidence_ids": ["EVID-003"]},
            {"level_code": "L02", "z_min": 106.0, "z_max": 109.0, "confidence": 0.91, "source_evidence_ids": ["EVID-003"]}
        ]

    candidates, anomalies, summary = orchestrator.run_inference_pipeline(
        parent_ulpin=parent_ulpin,
        actor_id="demo_scenario_loader",
        custom_levels=custom_levels
    )

    return {
        "status": "SCENARIO_LOADED",
        "scenario": scenario_key,
        "parent_ulpin": parent_ulpin,
        "candidates_count": len(candidates),
        "anomalies_count": len(anomalies),
        "summary": summary.model_dump()
    }

