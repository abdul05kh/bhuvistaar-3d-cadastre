# BhuVistaar — Field Simulation & Degraded Mode Specification

**Document Version**: 1.0.0  
**Scope**: Operational Simulation, Imperfect Field Conditions, AI Fallback, and Resiliency Safeguards

---

## 1. Purpose & Simulation Philosophy

Field data collection for 3D cadastre rarely occurs in pristine, laboratory environments. Operational conditions feature delayed survey transmissions, conflicting architectural measurements, missing elevation certificates, and temporary loss of connectivity.

BhuVistaar provides a controlled **Field Simulation Mode** to evaluate platform behavior under operational stress:

> [!NOTE]
> **DISCLOSURE OF SYNTHETIC NATURE**  
> All field simulation conditions described herein are **controlled prototype simulations**. They demonstrate deterministic error handling, non-destructive data recovery, and fail-safe governance. They do not represent empirical failure statistics from state survey departments.

---

## 2. Catalog of Simulated Scenarios

The platform provides 11 deterministic, resettable field scenarios accessible via `GET /api/v1/demo/scenarios` and the frontend Scenario Console:

| Scenario ID | Name | Injected Field Condition | Expected Platform Behavior |
|:---|:---|:---|:---|
| `clean` | **1. Clean Baseline** | Normal survey and architectural blueprints. | Generates 4 compliant floors (L01-L04). Passes Gate A and B with 0 blockers. |
| `defect` | **2. VRT-003 Vertical Overlap** | L01 ceiling (106.50m) physically intrudes 0.50m into L02 (106.00m). | Immediate Gate A `VRT-003` BLOCKER. AI Disagreement flagged. Gate C approval blocked. |
| `out_of_parcel` | **3. Boundary Breach** | Footprint shifted East outside parcel boundary. | Gate A `TOP-001` BLOCKER. Geometry is **not** silently clipped. Officer notified. |
| `missing_evidence` | **4. Unbacked Candidate** | Unit generation attempted without registered evidence. | Gate B `PROV-002` BLOCKER. Unverified candidates barred from approval. |
| `conflicting_evidence` | **5. Conflicting Evidence** | Arch plan (106.0m) contradicts Field Survey (106.5m). | Platform flags `EVIDENCE_CONFLICT` (0.50m delta). Halts automatic candidate promotion. |
| `ai_unavailable` | **6. Degraded AI Mode** | AI microservice disconnected (`AI_MODE=DISABLED`). | System logs fallback. Deterministic spatial validation & human governance remain 100% active. |
| `stale_evidence` | **7. Stale Evidence Protection** | Evidence replaced with altered SHA-256 hash after proposal. | Candidate flagged `STALE_EVIDENCE`. Reprocessing mandated before Gate C. |
| `stale_validation` | **8. Stale Validation Protection** | Spatial unit corrected after validation run completed. | Flagged `VALIDATION_OUTDATED`. Revalidation required before approval. |
| `review_rejection` | **9. Reviewer Discretionary Veto** | Reviewer rejects proposal due to unverified survey team. | Candidate status updated to `REJECTED`. Immutable audit log entry created. |
| `golden_workflow` | **10. Full Golden Workflow** | Complete lifecycle: ingestion → defect → correction → validation → approval → export. | End-to-end audit trail verified, resulting in export verified roundtrip. |
| `failure_recovery` | **11. Interrupted Upload Recovery** | Network drops midway through evidence registration. | Detects partial ingestion. Resumes safely. Duplicates blocked by SHA-256. |

---

## 3. Offline / Degraded Operations Safeguards

When AI assistance or remote survey APIs are disconnected:
1. **Zero Authoritative State Fabrication**: If the platform loses network connectivity, it prominently displays `CONNECTION LOST` and renders the `LAST VERIFIED STATE`. It never fabricates simulated updates.
2. **Deterministic Core Invariance**: Mathematical spatial rules (Shapely/PostGIS geometry validation, topology adjacency, volumetric calculations) execute locally and do not depend on external AI availability.
3. **Audit Tracking**: Every fallback activation generates an immutable audit record (`AI_FALLBACK_ACTIVATED`).

---

## 4. Failure Recovery Workflow

The failure recovery scenario demonstrates how BhuVistaar handles interrupted field evidence synchronization:
```
1. Operator begins bulk survey evidence upload.
2. Connection severed after registering first record (EVID-001).
   → System state: PARTIAL_INGESTION (clean database, no corrupted candidates).
3. Field operator reconnects and retries upload.
   → System resumes upload for remaining records (EVID-002, EVID-003).
4. System verifies SHA-256 checksum on duplicate attempts.
   → Re-upload of EVID-001 is recognized as duplicate and safely ignored.
5. Volumetric candidate generation proceeds only when all required evidence is present.
```
