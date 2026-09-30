# BHUVISTAAR — SLICE 4 SPECIFICATION
## Validation Intelligence, Explainability & Reproducibility Layer

---

### 0. Absolute Operating Principle
> **"Why should an engineer, reviewer, or government decision-maker trust this 3D cadastral candidate?"**
>
> BhuVistaar provides an unequivocal answer:
> **Do not trust machine learning blindly.**
> The system enforces absolute transparency:
>
> $$\text{Evidence} \longrightarrow \text{Observation} \longrightarrow \text{Candidate Proposal} \longrightarrow \mathbf{\text{Deterministic Geometry Engine}} \longrightarrow \mathbf{\text{Gate A/B Validation}} \longrightarrow \mathbf{\text{Disagreement Detection}} \longrightarrow \mathbf{\text{Human Review}} \longrightarrow \mathbf{\text{Governed Revision}} \longrightarrow \mathbf{\text{Gate C Approval}}$$

---

### 1. Architectural Boundaries & Non-Negotiables
- **AI Is NOT the Authority:** Machine proposals are strictly provisional (`status = "AI_CANDIDATE"`). Machine outputs cannot generate approved cadastral entities, cannot issue official ULPINs, cannot certify land ownership, and cannot bypass deterministic validation blockers.
- **Authoritative Persistence:** PostgreSQL 16 + PostGIS 3.4 is the sole persistence layer. No secondary databases or transient mock persistence are used in demo/production paths.
- **CRSs & Projections:** Demo domain coordinates are in explicit projected CRS `EPSG:32643` (WGS 84 / UTM zone 43N).
- **Prototype VUID Disclaimer:** Generated identifiers follow the deterministic specification `BV-{ulpin}-{unit_class}-{level_code}-{hash}` and carry the mandatory disclaimer:
  *"Prototype identifier — not an official 3D ULPIN."*

---

### 2. Core Capabilities Implemented in Slice 4

#### A. AI vs Validation Disagreement Engine (`backend/ai/services/disagreement_engine.py`)
Explicitly categorizes and records operational friction between machine proposals, deterministic spatial validators, and human officers:
- **CASE A: `AI_VALIDATION_DISAGREEMENT` (Severity: BLOCKER)**
  - Model proposes a candidate with high or medium confidence ($\ge 0.60$), but deterministic validation identifies a physical or topological blocker (e.g., `VRT-003` vertical stratum collision or `TOP-001` parcel boundary breach).
  - *Outcome:* Candidate approval is physically blocked by the deterministic engine. Human review and geometric correction are mandatory.
- **CASE B: `LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID` (Severity: WARNING)**
  - Model reports low confidence ($< 0.60$) due to degraded evidence scans or partial drawings, but deterministic validation passes with 0 blockers.
  - *Outcome:* Advisory warning flagged for reviewer inspection.
- **CASE C: `CONSISTENT` (Severity: INFO)**
  - Model confidence and deterministic validation rules agree.
- **CASE D: `HUMAN_OVERRIDE_OF_AI_PROPOSAL` (Severity: WARNING)**
  - Human officer rejects an AI candidate proposal (e.g. attic void erroneously classified as independent strata).
  - *Outcome:* Proposal preserved in history with officer rationale; permanently barred from promotion to governed unit.

#### B. Fact-Grounded Validation Explainability (`backend/ai/models/explainer.py`)
- Deep breakdown of geometric and topological failures:
  - **`VRT-003` Breakdown:** Computes exact physical overlap (e.g. Level L01 ceiling at 106.50m vs Level L02 floor at 106.00m $\to$ -0.50m gap violating the -0.001m tolerance threshold). Explains physical collision and suggests field survey remediation.
  - **`TOP-001` Breakdown:** Identifies exact vertex coordinates extending beyond the parent parcel polygon.
  - **`GEO-002` Breakdown:** Explains self-intersection locations and ring orientation errors.
- **Zero Hallucination Guarantee:** The explainability engine operates strictly on database-recorded metrics and measured facts. Free-form hallucination of non-existent spatial boundaries is architecturally prevented.

#### C. Cryptographic Reproducibility Snapshots (`backend/ai/services/reproducibility_service.py`)
- Computes deterministic SHA-256 snapshot hashes over:
  - Source evidence IDs and SHA-256 content checksums
  - Polygon footprint coordinates and vertical intervals ($z_{min}, z_{max}$)
  - Canonical CRS (`EPSG:32643`)
  - Model metadata (`prismatic-candidate-001` v0.1.0) and model configuration hash
  - Validation ruleset version (`1.0.0`)
  - Software git commit hash (`ab35dd2`)
- **Status Ratings:**
  - `REPRODUCIBLE`: 100% of input evidence checksums, geometric vertices, model versions, and ruleset versions are pinned and verified.
  - `PARTIALLY_REPRODUCIBLE`: Some external metadata or unpinned versions present.
  - `NOT_REPRODUCIBLE`: Missing evidence hashes or unversioned models.
- **Verification API:** Recomputes snapshot hash dynamically from current database state to prove tamper-resistance.

#### D. Model Comparison Engine (`backend/ai/services/model_comparison_service.py`)
- Enables side-by-side empirical comparison between candidate generators:
  - Model A: `prismatic-candidate-001` (v0.1.0)
  - Model B: `cadastral-heuristic-baseline-001` (v0.0.1-baseline)
- Compares: candidate granularity, mean confidence, anomaly triage, validation blocker detection rates, and evidence traceability.
- **Strict Anti-Hype Policy:** Reports only measured behavioral differences ("Difference observed"). Claims of statistical superiority are prohibited without third-party benchmarks on operational national survey records.

#### E. 10-Scenario Deterministic Evaluation Harness (`backend/ai/evaluators/evaluator.py`)
Benchmarked against 10 controlled synthetic scenarios:
1. `1_CLEAN`: Standard 4-level contiguous sequence
2. `2_VRT_003_OVERLAP`: L01/L02 0.50m vertical collision (defect fixture)
3. `3_OUT_OF_PARCEL`: Candidate footprint extending 2.5m beyond parcel boundary
4. `4_INVALID_GEOMETRY`: Self-intersecting figure-8 bowtie polygon
5. `5_MISSING_EVIDENCE`: Proposal lacking source document linkage
6. `6_CONFLICTING_EVIDENCE`: Discordant elevation marks between architectural drawing and survey
7. `7_LOW_CONFIDENCE_OBSERVATION`: Weak hand-drawn sketch candidate (0.45 confidence)
8. `8_AI_HIGH_CONF_BUT_INVALID`: High confidence AI proposal with hidden geometric overlap
9. `9_AI_LOW_CONF_BUT_VALID`: Low confidence proposal that is geometrically clean
10. `10_HUMAN_REJECTED_CANDIDATE`: Human officer overrides AI proposal

#### F. AI Service Failure & Offline Fallback Mode
- Toggleable via `AI_ASSISTANCE_ENABLED` in `backend/config.py`.
- When disabled (`AI_ASSISTANCE_ENABLED=false`):
  - Deterministic spatial extrusion, Gate A/B validation, human review, non-destructive correction, Gate C approval, append-only audit trail, and structured JSON export continue running at 100% functionality without crashes or degradation.

---

### 3. Database Schema Changes (Alembic Migration 004)
Applied migration: `alembic/versions/004_validation_intelligence_and_reproducibility.py`
- `validation_disagreements`: Stores categorized Case A/B/C/D disagreements, measured values, thresholds, and affected rule codes.
- `reproducibility_snapshots`: Stores cryptographic snapshot hashes, pinned evidence checksums, model configuration hashes, ruleset versions, and software commit references.
- `evaluation_runs`: Stores historical benchmark results, metrics, execution times, and disagreement counts.

---

### 4. API Endpoints Reference
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ai/disagreements/{ulpin}` | Catalogs AI vs Validation disagreements for a parcel |
| `GET` | `/api/v1/ai/explain/validation/{run_id}` | Detailed human-readable breakdown of validation rules |
| `GET` | `/api/v1/ai/reproducibility/{target_id}` | Generates/retrieves cryptographic reproducibility snapshot |
| `POST` | `/api/v1/ai/reproducibility/verify` | Re-verifies cryptographic snapshot hash against database state |
| `POST` | `/api/v1/ai/models/compare` | Compares model versions and heuristic baselines |
| `GET` | `/api/v1/ai/evaluations/history` | Historical evaluation benchmark runs |
| `POST` | `/api/v1/ai/evaluate` | Executes 10-scenario empirical evaluation harness |

---

### 5. Automated Verification Results
- **Backend Test Suite (Pytest 9.1.1, Python 3.12.10):**
  - **56 / 56 tests passed (100%) in 6.88 seconds.**
  - Coverage includes: Slice 1A geometry & PostGIS, Slice 1B governance & audit, Slice 2 interactive workspace, Slice 3 AI pipeline, Slice 4 disagreements, reproducibility snapshots, ruleset versioning, model comparison, and failure injection resilience.
- **Frontend Production Build (Vite 8.3.1, TypeScript 5.9):**
  - Built cleanly in 319ms with 0 type errors.

---

### 6. Golden Slice 4 Walkthrough for Judges
1. Open parent ULPIN `12345678901234`.
2. Notice the top header indicates: `AI: 4 Cand • 1 Anom • 1 Disagreement`.
3. Open the **Disagreements** tab:
   - See **CASE A: AI / Validation Disagreement** on Level L02.
   - Machine model proposed L02 with 0.91 confidence based on `EVID-003`.
   - Deterministic spatial validator detects `VRT-003` blocker (0.50m overlap with L01).
   - Approval is physically blocked by the geometry engine.
4. Click **[Explain Why]**:
   - Opens the Validation Explanation modal detailing the physical overlap: Lower ceiling 106.50m vs Upper floor 106.00m $\to$ -0.500m gap ($< -0.001\text{m}$ tolerance).
5. Open the **Side-by-Side Triad** tab:
   - View Evidence (`EVID-003`) $\longleftrightarrow$ Candidate Proposal ($106.0\text{m} \to 109.0\text{m}$) $\longleftrightarrow$ Deterministic Blocker.
6. Click **[Reproducibility Snapshot]**:
   - Displays cryptographic SHA-256 snapshot hash, pinned evidence checksums, model configuration hash, ruleset v1.0.0, and commit reference `ab35dd2`.
   - Click **[Verify Cryptographic Hash]** $\to$ Dynamic verification confirms 100% deterministic reproducibility.
7. Click **[Compare Models]** in header:
   - Displays side-by-side empirical metrics between `prismatic-candidate-001` and heuristic baseline with transparent disclosure of synthetic benchmark scope.
8. Non-destructive Correction & Human Governance:
   - Officer submits correction: L01 ceiling adjusted from 106.50m to 106.00m.
   - New revision created with newly generated Prototype VUID.
   - Revalidation succeeds (0 blockers).
   - Officer accepts revision $\to$ Gate C approval unlocked $\to$ Structured export generated.
