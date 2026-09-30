# BhuVistaar — Public Claims & Evidence Register

This register enforces strict anti-hype standards. Every public technical claim made regarding BhuVistaar is categorized by its verification type and documented evidence.

---

## Verification Classifications
1. `DETERMINISTIC VERIFIED`: Mathematically or architecturally enforced in code with zero stochastic uncertainty.
2. `AUTOMATED TEST`: Verified by automated test suites passing in CI / local test runners against live databases.
3. `BROWSER VERIFIED`: Verified via headless browser automated interaction (Playwright).
4. `SYNTHETIC EVALUATION`: Tested against controlled synthetic cadastral scenarios, not real-world field statistics.
5. `SIMULATED`: Operational behavior simulated in prototype code; does not represent production infrastructure.
6. `DOCUMENTED DESIGN`: Architecturally specified for future implementation.
7. `FUTURE`: Beyond current prototype scope.

---

## Claims & Evidence Register

| Claim ID | Public Technical Claim | Verification Type | Concrete Evidence in Repository | Documented Prototype Limitation |
|---|---|---|---|---|
| **CLM-001** | Parent 14-digit ULPIN is never mutated or altered by 3D operations. | `DETERMINISTIC VERIFIED` | `backend/domain/parent_parcel.py`, `backend/services/parcel_service.py` | Parent ULPIN is an immutable foreign key root in `spatial_units`. |
| **CLM-002** | Prototype VUID generation is deterministic and representation-invariant. | `AUTOMATED TEST` | `tests/unit/test_vuid_determinism.py`, `test_canonical_normalization.py` | Polygon vertex order or ring direction changes yield the exact same SHA-256 digest. |
| **CLM-003** | Gate A detects vertical collisions (VRT-003) and parent breaches (TOP-001) as BLOCKERS. | `AUTOMATED TEST` | `tests/unit/test_vrt_003_contract.py`, `tests/integration/test_slice1a_pipeline.py` | Blocks approval without silently auto-clipping geometry. |
| **CLM-004** | AI candidate proposals cannot autonomously approve or modify cadastral records. | `DETERMINISTIC VERIFIED` | `backend/services/approval_service.py`, `tests/unit/test_slice6_governance_negative.py` | Attempting approval with `actor_context="AI_AUTONOMOUS"` raises `ApprovalBlockedError`. |
| **CLM-005** | Corrections spawn new revisions without destroying predecessor versions. | `AUTOMATED TEST` | `backend/services/correction_service.py`, `tests/integration/test_slice1b_governance_postgis.py` | Revision 1 remains intact in PostgreSQL; Revision 2 links predecessor ID. |
| **CLM-006** | Gate C approval is strictly blocked when unresolved BLOCKER issues exist. | `AUTOMATED TEST` | `backend/services/approval_service.py`, `tests/integration/test_slice1b_api_workflow.py` | HTTP 409 Conflict returned if `blocker_count > 0`. |
| **CLM-007** | Validation explainability uses recorded physical measurements with zero hallucination. | `DETERMINISTIC VERIFIED` | `backend/ai/services/explainability_service.py` | Calculates exact gap (`observed_gap = -0.50m`) from database entities without LLM inference. |
| **CLM-008** | Stale validations and modified evidence automatically invalidate approval eligibility. | `AUTOMATED TEST` | `tests/unit/test_slice5_operational.py`, `tests/unit/test_slice6_governance_negative.py` | `VALIDATION_OUTDATED` and `STALE_EVIDENCE` checks prevent approval on outdated passes. |
| **CLM-009** | Interoperability exports produce valid JSON v1.0.0, 2D GeoJSON, and 3D OBJ meshes with round-trip integrity. | `AUTOMATED TEST` | `backend/services/interoperability_service.py`, `tests/integration/test_slice5_integration.py` | Round-trip verification endpoint returns `status: MATCH`. |
| **CLM-010** | End-to-end interactive workflow functions in a real browser. | `BROWSER VERIFIED` | `tests/e2e/test_slice5_browser_e2e.py` | Playwright executes 14-step inspection, correction, and export flow in real browser. |
| **CLM-011** | Field simulation models operational disruptions (interrupted upload, offline AI, conflicting survey). | `SIMULATED` | `backend/services/field_simulation_service.py`, `docs/field-simulation.md` | Simulations demonstrate platform recovery; they are NOT empirical field failure statistics. |
| **CLM-012** | Model evaluation benchmark scores (Precision, Recall, F1). | `SYNTHETIC EVALUATION` | `backend/ai/evaluators/benchmark_harness.py`, `docs/evaluation.md` | Labeled `SYNTHETIC_PROTOTYPE_EVALUATION`; does NOT represent real-world ML accuracy. |
| **CLM-013** | Role-based authorization boundaries (Viewer, Reviewer, Approver). | `SIMULATED` | `backend/schemas/governance_contracts.py`, `docs/security.md` | Simulated via HTTP headers (`SIMULATED_PROTOTYPE`); not production OIDC/Keycloak authentication. |
| **CLM-014** | Integration with statutory land registry portals (Bhoomi, Dharani, CORD). | `FUTURE` | `docs/prototype-vs-mvp.md`, `docs/limitations.md` | **NOT IMPLEMENTED**. BhuVistaar is an interoperability-ready prototype, not a connected government database. |
| **CLM-015** | Legal title adjudication or boundary guarantee. | `NOT APPLICABLE` | Prominent UI / API disclaimers | BhuVistaar validates spatial geometry; it does not adjudicate ownership or replace statutory land courts. |
