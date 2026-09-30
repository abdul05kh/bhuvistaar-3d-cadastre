# BhuVistaar — Subsystem Capability Status Matrix

This matrix summarizes the verified status of all functional modules across Slices 1A through 6.

---

## Maturity Legend
- **VERIFIED:** Fully implemented in source code and proven by automated tests against live PostGIS database.
- **PROTOTYPE:** Implemented for demonstration scope; calibrated on synthetic fixtures.
- **SIMULATED:** Simulated in software to demonstrate operational behavior without external dependencies.
- **SYNTHETIC:** Evaluated against controlled synthetic scenarios; does not represent measured real-world statistics.
- **NOT IMPLEMENTED:** Explicitly out of scope for the hackathon prototype.

---

## Capability Status Matrix

| Subsystem | Functional Capability | Implementation Status | Test Coverage | Operational Evidence |
|---|---|---|---|---|
| **Spatial Core** | Parent Parcel Management | **VERIFIED** | Unit & Integration | `parent_parcels` table, SRID 32643 geometry |
| | Representation-Invariant VUID | **VERIFIED** | Unit Tests | `tests/unit/test_vuid_determinism.py` |
| | Canonical Geometry Normalization | **VERIFIED** | Unit Tests | `tests/unit/test_canonical_normalization.py` |
| | Volumetric Prismatic Extrusion | **VERIFIED** | Unit Tests | `tests/unit/test_geometry_extrusion.py` |
| **Validation Core** | Gate A Boundary Containment (`TOP-001`) | **VERIFIED** | Integration Tests | Blocks encroachments without auto-clipping |
| | Gate A Vertical Overlap Blocker (`VRT-003`) | **VERIFIED** | Integration Tests | `tests/unit/test_vrt_003_contract.py` |
| | Gate B Provenance Integrity (`PROV-001..004`) | **VERIFIED** | Integration Tests | `tests/integration/test_slice1b_governance_postgis.py` |
| **AI Layer** | Prismatic Extrusion Candidate Model | **PROTOTYPE** | Unit & Benchmark | `backend/ai/models/candidate_prismatic.py` |
| | Cadastral Anomaly Detector | **PROTOTYPE** | Unit & Benchmark | `backend/ai/models/anomaly_detector.py` |
| | AI vs Validation Disagreement Engine | **VERIFIED** | Unit Tests | `tests/unit/test_validation_disagreement.py` |
| | Fact-Grounded Explainability | **VERIFIED** | Integration Tests | `backend/ai/services/explainability_service.py` |
| | 10-Scenario Synthetic Evaluation | **SYNTHETIC** | Automated Harness | `backend/ai/evaluators/benchmark_harness.py` |
| **Governance Core** | Human Review Workflow (ACCEPT / REVISE / REJECT) | **VERIFIED** | Integration Tests | `review_records` table, Review Workspace UI |
| | Non-Destructive Revisioning | **VERIFIED** | Integration Tests | Spawns Rev 2; preserves Rev 1 intact |
| | Gate C Adjudication Engine | **VERIFIED** | Integration Tests | Rejects approval if blockers or unreviewed |
| | Append-Only Audit Trail | **VERIFIED** | Integration Tests | `audit_events` table with correlation IDs |
| **Operational Layer**| Containerized Docker Deployment | **VERIFIED** | Docker Compose | `docker-compose.yml`, `Dockerfile.frontend` |
| | Tri-Level Health Probes | **VERIFIED** | Integration Tests | `GET /health/ready` |
| | Evidence Quality Gate | **VERIFIED** | Unit Tests | `POST /api/v1/evidence/quality/check` |
| | Stale Validation & Evidence Protection | **VERIFIED** | Unit Tests | `tests/unit/test_slice5_operational.py` |
| | 11 Field Simulation Scenarios | **SIMULATED** | Integration Tests | `POST /api/v1/demo/scenarios/{id}/execute` |
| | Role-Based Authorization Model | **SIMULATED** | Integration Tests | `tests/unit/test_slice6_governance_negative.py` |
| | Non-Destructive Data Integrity Checker | **VERIFIED** | Automated Script | `backend/db/bootstrap.py` |
| | Database Backup & Restore Procedure | **VERIFIED** | Automated Script | `scripts/backup_restore_simulation.py` |
| **Interoperability** | Prototype JSON v1.0.0 Export | **VERIFIED** | Integration Tests | Full schema with provenance and audit |
| | 2D GeoJSON FeatureCollection (RFC 7946) | **VERIFIED** | Integration Tests | `GET /api/v1/export/geojson/{ulpin}` |
| | 3D Wavefront OBJ Mesh Export | **VERIFIED** | Integration Tests | `GET /api/v1/export/3d/{id}` |
| | Import / Export Round-Trip Verification | **VERIFIED** | Integration Tests | `POST /api/v1/export/roundtrip/verify` (`MATCH`) |
| **External Systems** | State Land Registry Direct Connection | **NOT IMPLEMENTED** | None | Out of scope for prototype |
| | Statutory 3D ULPIN Minting Authority | **NOT IMPLEMENTED** | None | Out of scope for prototype |
| | Real-World Empirical Field Accuracy | **NOT IMPLEMENTED** | None | Synthetic evaluation only |
