# BhuVistaar — Full Architecture & Operational Traceability

This document traces user actions through the complete stack: Frontend Screen $\to$ REST API $\to$ Application Service $\to$ Database Entity $\to$ Audit Trail Event.

---

## 1. Golden Operational Traceability Matrix

| User Action | Frontend Component | REST API Endpoint | Backend Service Method | Database Entities Mutated | Emitted Audit Event |
|---|---|---|---|---|---|
| **Ingest Evidence File** | `EvidencePanel.tsx` / `FieldOperatorView.tsx` | `POST /api/v1/evidence/` | `EvidenceService.register_evidence()` | `evidence_records` (INSERT) | `EVIDENCE_REGISTERED` |
| **Check Pre-Flight Quality** | `FieldOperatorView.tsx` | `POST /api/v1/evidence/quality/check` | `EvidenceService.evaluate_quality()` | None (Pure In-Memory Evaluation) | N/A |
| **Trigger Candidate Generation** | `AISuggestionsPanel.tsx` | `POST /api/v1/ai/candidates/generate` | `CandidateGenerationService.generate_prismatic_candidates()` | `ai_candidates` (INSERT) | `AI_CANDIDATE_GENERATED` |
| **Run Deterministic Validation** | `ValidationCenter.tsx` | `POST /api/v1/validation/run/{ulpin}` | `ValidationService.run_gate_a_validation()` | `validation_runs`, `validation_issues` (INSERT) | `VALIDATION_RUN_EXECUTED` |
| **Inspect Overlap Explanation** | `ValidationExplanationModal.tsx` | `GET /api/v1/validation/runs/{run_id}/explain` | `ExplainabilityService.explain_validation_run()` | None (Read Only) | None |
| **Examine Disagreements** | `DisagreementTracker.tsx` | `GET /api/v1/ai/disagreements/{ulpin}` | `DisagreementEngine.evaluate_disagreements()` | `disagreement_records` (INSERT) | `DISAGREEMENT_RECORDED` |
| **Submit Correction Request** | `ReviewWorkspace.tsx` | `POST /api/v1/reviews/units/{vuid}/revisions/{id}` | `ReviewService.submit_review()` | `review_records` (INSERT) | `REVIEW_SUBMITTED` |
| **Execute Non-Destructive Correction** | `CorrectionModal.tsx` | `POST /api/v1/units/{vuid}/revisions/{id}/correct` | `CorrectionService.apply_correction()` | `spatial_unit_revisions` (INSERT Rev 2) | `REVISION_CREATED` |
| **Submit Officer Sign-Off (ACCEPT)** | `ReviewWorkspace.tsx` | `POST /api/v1/reviews/units/{vuid}/revisions/{id}` | `ReviewService.submit_review()` | `review_records` (INSERT) | `REVIEW_SUBMITTED` |
| **Execute Gate C Approval** | `AppHeader.tsx` / `ReviewWorkspace.tsx` | `POST /api/v1/governance/approval/{revision_id}` | `ApprovalService.approve_revision()` | `approval_decisions` (INSERT), `spatial_units` (UPDATE active_rev) | `APPROVAL_GRANTED` |
| **Export Structured JSON** | `ExportCenter.tsx` / `InteroperabilityExportModal.tsx` | `GET /api/v1/export/{ulpin}/units/{vuid}` | `ExportService.export_unit_revision()` | None (Serialization) | `EXPORT_GENERATED` |
| **Export 2D GeoJSON** | `InteroperabilityExportModal.tsx` | `GET /api/v1/export/geojson/{ulpin}` | `InteroperabilityService.export_geojson()` | None (Serialization) | `EXPORT_GENERATED` |
| **Export 3D Wavefront OBJ** | `InteroperabilityExportModal.tsx` | `GET /api/v1/export/3d/{revision_id}` | `InteroperabilityService.export_3d_obj()` | None (Serialization) | `EXPORT_GENERATED` |
| **Verify Round-Trip Integrity** | `InteroperabilityExportModal.tsx` | `POST /api/v1/export/roundtrip/verify` | `InteroperabilityService.verify_round_trip()` | None (Verification) | None |
| **Verify System Readiness** | `SystemReadinessModal.tsx` | `GET /api/v1/system/readiness` | `EndpointsSystem.get_readiness_status()` | Live PostGIS ping & DB checks | None |
| **Run Data Integrity Audit** | `SystemReadinessModal.tsx` | `GET /api/v1/system/integrity` | `bootstrap.verify_data_integrity()` | Live table scans | None |
| **Execute Field Simulation** | `DemoScenarioBar.tsx` | `POST /api/v1/demo/scenarios/{id}/execute` | `FieldSimulationService.execute_scenario()` | Full synthetic scenario seed | `FIELD_SIMULATION_EXECUTED` |
| **Reset Demo State** | `AppHeader.tsx` / `DemoScenarioBar.tsx` | `POST /api/v1/demo/reset` | `EndpointsDemo.reset_demo_state()` | Re-seeds synthetic clean/defect fixtures | `DEMO_RESET` |
